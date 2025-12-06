from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers_new import RegisterSerializer, UserProfileSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class PasswordResetRequestView(APIView):
    """Request password reset (sends email in production)"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            # In production, send email with reset token
            # For now, just return success
            return Response({
                'message': 'Password reset instructions sent to your email'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({
                'message': 'Password reset instructions sent to your email'
            }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """Confirm password reset with token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # In production, validate token and reset password
        # For now, just return success
        return Response({
            'message': 'Password reset successful'
        }, status=status.HTTP_200_OK)
