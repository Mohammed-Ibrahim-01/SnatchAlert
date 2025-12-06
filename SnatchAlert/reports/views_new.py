from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import IncidentFact, IMEIRegistry, AreaAlert
from core.models import LocationDim
from .serializers_new import (
    IncidentFactCreateSerializer, IncidentFactListSerializer, IncidentFactUpdateSerializer,
    IMEIRegistrySerializer, IMEICheckSerializer, AreaAlertSerializer,
    CrimeHeatmapSerializer, AreaSafetySerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrAuthority


class IncidentCreateView(generics.CreateAPIView):
    """Create a new incident report"""
    serializer_class = IncidentFactCreateSerializer
    permission_classes = [permissions.AllowAny]  # Allow anonymous reporting
    
    def perform_create(self, serializer):
        serializer.save()


class IncidentListView(generics.ListAPIView):
    """List all incidents with filtering"""
    serializer_class = IncidentFactListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['incident_type__category', 'status', 'location__city', 'location__district', 'fir_filed']
    search_fields = ['description', 'location__city', 'location__district', 'incident_type__category']
    ordering_fields = ['occurred_at', 'created_at']
    ordering = ['-occurred_at']
    
    def get_queryset(self):
        queryset = IncidentFact.objects.select_related(
            'location', 'victim', 'incident_type', 'stolen_item', 'reported_by'
        ).all()
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(occurred_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(occurred_at__lte=date_to)
        
        # Filter by neighborhood
        neighborhood = self.request.query_params.get('neighborhood')
        if neighborhood:
            queryset = queryset.filter(location__neighborhood__icontains=neighborhood)
        
        return queryset


class IncidentDetailView(generics.RetrieveAPIView):
    """Get incident details"""
    serializer_class = IncidentFactListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = IncidentFact.objects.select_related(
        'location', 'victim', 'incident_type', 'stolen_item', 'reported_by'
    ).all()


class IncidentUpdateView(generics.UpdateAPIView):
    """Update an incident report"""
    serializer_class = IncidentFactUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = IncidentFact.objects.all()


class IncidentDeleteView(generics.DestroyAPIView):
    """Delete an incident report"""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = IncidentFact.objects.all()


class MyIncidentsView(generics.ListAPIView):
    """List incidents reported by current user"""
    serializer_class = IncidentFactListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return IncidentFact.objects.filter(
            reported_by=self.request.user
        ).select_related('location', 'victim', 'incident_type', 'stolen_item').order_by('-created_at')


# IMEI Tracking Views
class IMEIRegisterView(generics.CreateAPIView):
    """Register a stolen phone IMEI"""
    serializer_class = IMEIRegistrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


class IMEICheckView(APIView):
    """Check if an IMEI is stolen"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = IMEICheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        imei = serializer.validated_data['imei']
        
        try:
            record = IMEIRegistry.objects.get(imei=imei)
            return Response({
                'found': True,
                'status': record.status,
                'phone_brand': record.phone_brand,
                'phone_model': record.phone_model,
                'reported_at': record.reported_at,
                'message': f'This IMEI is registered as {record.status}'
            })
        except IMEIRegistry.DoesNotExist:
            return Response({
                'found': False,
                'message': 'This IMEI is not in our stolen registry'
            })


class IMEIListView(generics.ListAPIView):
    """List all registered IMEIs (admin only)"""
    serializer_class = IMEIRegistrySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAuthority]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['imei', 'phone_brand', 'phone_model', 'owner_name']
    queryset = IMEIRegistry.objects.all().order_by('-reported_at')


class IMEIUpdateView(generics.UpdateAPIView):
    """Update IMEI status (admin only)"""
    serializer_class = IMEIRegistrySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAuthority]
    queryset = IMEIRegistry.objects.all()


# Crime Heatmap & Analytics Views
class CrimeHeatmapView(APIView):
    """Get crime hotspots for heatmap visualization"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # Get query parameters
        days = int(request.query_params.get('days', 30))
        city = request.query_params.get('city')
        
        # Calculate date threshold
        date_threshold = timezone.now() - timedelta(days=days)
        
        # Query incidents grouped by location
        queryset = IncidentFact.objects.filter(occurred_at__gte=date_threshold)
        
        if city:
            queryset = queryset.filter(location__city__iexact=city)
        
        # Group by location and count
        heatmap_data = queryset.values(
            'location__latitude',
            'location__longitude',
            'location__city',
            'location__district'
        ).annotate(
            incident_count=Count('id')
        ).filter(
            location__latitude__isnull=False,
            location__longitude__isnull=False
        ).order_by('-incident_count')
        
        serializer = CrimeHeatmapSerializer(heatmap_data, many=True)
        return Response(serializer.data)


class AreaSafetyScoreView(APIView):
    """Calculate safety scores for areas"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        city = request.query_params.get('city')
        days = int(request.query_params.get('days', 90))
        
        date_threshold = timezone.now() - timedelta(days=days)
        
        # Get incident counts by location
        queryset = IncidentFact.objects.filter(occurred_at__gte=date_threshold)
        
        if city:
            queryset = queryset.filter(location__city__iexact=city)
        
        area_stats = queryset.values(
            'location__id',
            'location__city',
            'location__district',
            'location__neighborhood'
        ).annotate(
            incident_count=Count('id')
        ).order_by('-incident_count')
        
        # Calculate safety scores (100 - normalized incident count)
        max_incidents = area_stats[0]['incident_count'] if area_stats else 1
        
        results = []
        for area in area_stats:
            incident_count = area['incident_count']
            # Safety score: 100 (safest) to 0 (most dangerous)
            safety_score = max(0, 100 - (incident_count / max_incidents * 100))
            
            # Risk level classification
            if safety_score >= 80:
                risk_level = 'Low'
            elif safety_score >= 60:
                risk_level = 'Medium'
            elif safety_score >= 40:
                risk_level = 'High'
            else:
                risk_level = 'Critical'
            
            results.append({
                'location_id': area['location__id'],
                'city': area['location__city'],
                'district': area['location__district'],
                'neighborhood': area['location__neighborhood'],
                'incident_count': incident_count,
                'safety_score': round(safety_score, 2),
                'risk_level': risk_level
            })
        
        serializer = AreaSafetySerializer(results, many=True)
        return Response(serializer.data)


class CrimeStatisticsView(APIView):
    """Get overall crime statistics"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        date_threshold = timezone.now() - timedelta(days=days)
        
        queryset = IncidentFact.objects.filter(occurred_at__gte=date_threshold)
        
        # Overall stats
        total_incidents = queryset.count()
        
        # By incident type
        by_type = queryset.values('incident_type__category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # By city
        by_city = queryset.values('location__city').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # FIR filed percentage
        fir_filed_count = queryset.filter(fir_filed=True).count()
        fir_percentage = (fir_filed_count / total_incidents * 100) if total_incidents > 0 else 0
        
        return Response({
            'total_incidents': total_incidents,
            'period_days': days,
            'by_incident_type': list(by_type),
            'top_cities': list(by_city),
            'fir_filed_percentage': round(fir_percentage, 2)
        })


# Area Alerts Views
class AreaAlertListView(generics.ListAPIView):
    """List active area alerts"""
    serializer_class = AreaAlertSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['alert_type', 'severity', 'location__city']
    
    def get_queryset(self):
        return AreaAlert.objects.filter(
            is_active=True,
            valid_from__lte=timezone.now()
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=timezone.now())
        ).select_related('location').order_by('-severity', '-created_at')


class AreaAlertCreateView(generics.CreateAPIView):
    """Create area alert (admin only)"""
    serializer_class = AreaAlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAuthority]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AreaAlertUpdateView(generics.UpdateAPIView):
    """Update area alert (admin only)"""
    serializer_class = AreaAlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAuthority]
    queryset = AreaAlert.objects.all()


class AreaAlertDeleteView(generics.DestroyAPIView):
    """Delete area alert (admin only)"""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAuthority]
    queryset = AreaAlert.objects.all()
