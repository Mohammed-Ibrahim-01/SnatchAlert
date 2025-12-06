from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Custom user model with role-based access"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('authority', 'Authority'),
    ]
    
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_verified = models.BooleanField(default=False)
    address = models.TextField(blank=True)
    
    class Meta:
        db_table = 'custom_user'

    def __str__(self):
        return self.username
    
    def is_admin_or_authority(self):
        return self.role in ['admin', 'authority']
