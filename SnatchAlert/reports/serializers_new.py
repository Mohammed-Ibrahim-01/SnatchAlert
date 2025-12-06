from rest_framework import serializers
from django.db import transaction
from .models import IncidentFact, IMEIRegistry, AreaAlert
from core.models import LocationDim, VictimDim, IncidentTypeDim, StolenItemDim
from core.serializers import LocationDimSerializer, VictimDimSerializer, IncidentTypeDimSerializer, StolenItemDimSerializer


class IncidentFactCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating incident reports"""
    location_data = LocationDimSerializer(write_only=True)
    victim_data = VictimDimSerializer(write_only=True, required=False)
    incident_type_name = serializers.CharField(write_only=True)
    stolen_item_data = StolenItemDimSerializer(write_only=True, required=False)
    
    class Meta:
        model = IncidentFact
        fields = [
            'id', 'occurred_at', 'location_data', 'victim_data', 'incident_type_name',
            'stolen_item_data', 'value_estimate', 'fir_filed', 'description',
            'is_anonymous', 'fir_document', 'item_image', 'status'
        ]
        read_only_fields = ['id', 'reported_by', 'created_at', 'updated_at']
    
    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        
        # Extract nested data
        location_data = validated_data.pop('location_data')
        victim_data = validated_data.pop('victim_data', None)
        incident_type_name = validated_data.pop('incident_type_name')
        stolen_item_data = validated_data.pop('stolen_item_data', None)
        
        # Create or get location
        location, _ = LocationDim.objects.get_or_create(
            city=location_data['city'],
            district=location_data.get('district', ''),
            neighborhood=location_data.get('neighborhood', ''),
            street_address=location_data.get('street_address', ''),
            defaults={
                'province': location_data.get('province', ''),
                'latitude': location_data.get('latitude'),
                'longitude': location_data.get('longitude'),
            }
        )
        
        # Create or get incident type
        incident_type, _ = IncidentTypeDim.objects.get_or_create(
            category=incident_type_name,
            defaults={'description': f'{incident_type_name} incident'}
        )
        
        # Create victim if data provided
        victim = None
        if victim_data and not validated_data.get('is_anonymous', False):
            victim = VictimDim.objects.create(
                user=request.user if request and request.user.is_authenticated else None,
                **victim_data
            )
        
        # Create stolen item if data provided
        stolen_item = None
        if stolen_item_data:
            stolen_item = StolenItemDim.objects.create(**stolen_item_data)
        
        # Create incident
        incident = IncidentFact.objects.create(
            location=location,
            victim=victim,
            incident_type=incident_type,
            stolen_item=stolen_item,
            reported_by=request.user if request and request.user.is_authenticated else None,
            **validated_data
        )
        
        return incident


class IncidentFactListSerializer(serializers.ModelSerializer):
    """Serializer for listing incidents"""
    location = LocationDimSerializer(read_only=True)
    victim = VictimDimSerializer(read_only=True)
    incident_type = IncidentTypeDimSerializer(read_only=True)
    stolen_item = StolenItemDimSerializer(read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    
    class Meta:
        model = IncidentFact
        fields = [
            'id', 'occurred_at', 'location', 'victim', 'incident_type', 'stolen_item',
            'value_estimate', 'fir_filed', 'description', 'is_anonymous', 'status',
            'fir_document', 'item_image', 'reported_by_username', 'created_at', 'updated_at'
        ]


class IncidentFactUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating incidents"""
    class Meta:
        model = IncidentFact
        fields = ['description', 'status', 'fir_filed', 'fir_document', 'item_image']


class IMEIRegistrySerializer(serializers.ModelSerializer):
    """Serializer for IMEI registry"""
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    incident_id = serializers.IntegerField(source='incident.id', read_only=True)
    
    class Meta:
        model = IMEIRegistry
        fields = [
            'id', 'imei', 'phone_brand', 'phone_model', 'owner_name', 'owner_contact',
            'incident', 'incident_id', 'status', 'reported_at', 'updated_at',
            'reported_by', 'reported_by_username', 'notes'
        ]
        read_only_fields = ['reported_by', 'reported_at', 'updated_at']
    
    def validate_imei(self, value):
        if len(value) not in [15, 17]:
            raise serializers.ValidationError("IMEI must be 15 or 17 digits")
        return value


class IMEICheckSerializer(serializers.Serializer):
    """Serializer for checking IMEI status"""
    imei = serializers.CharField(max_length=20)
    
    def validate_imei(self, value):
        if len(value) not in [15, 17]:
            raise serializers.ValidationError("IMEI must be 15 or 17 digits")
        return value


class AreaAlertSerializer(serializers.ModelSerializer):
    """Serializer for area alerts"""
    location = LocationDimSerializer(read_only=True)
    location_id = serializers.IntegerField(write_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = AreaAlert
        fields = [
            'id', 'location', 'location_id', 'alert_type', 'message', 'severity',
            'is_active', 'valid_from', 'valid_until', 'created_by', 'created_by_username', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']


class CrimeHeatmapSerializer(serializers.Serializer):
    """Serializer for crime heatmap data"""
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    incident_count = serializers.IntegerField()
    city = serializers.CharField()
    district = serializers.CharField()


class AreaSafetySerializer(serializers.Serializer):
    """Serializer for area safety scores"""
    location_id = serializers.IntegerField()
    city = serializers.CharField()
    district = serializers.CharField()
    neighborhood = serializers.CharField()
    incident_count = serializers.IntegerField()
    safety_score = serializers.FloatField()
    risk_level = serializers.CharField()
