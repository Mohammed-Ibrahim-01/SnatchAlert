from django.db import models
from django.core.validators import FileExtensionValidator

class IncidentFact(models.Model):
    """Fact table for crime incidents - follows snowflake schema"""
    
    # Timestamp when incident occurred
    occurred_at = models.DateTimeField(null=True, blank=True)
    
    # Foreign Keys to Dimension Tables (Snowflake Schema)
    location = models.ForeignKey("core.LocationDim", on_delete=models.CASCADE, related_name='incidents')
    victim = models.ForeignKey("core.VictimDim", on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    incident_type = models.ForeignKey("core.IncidentTypeDim", on_delete=models.CASCADE, related_name='incidents')
    stolen_item = models.ForeignKey("core.StolenItemDim", on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    
    # Fact Measures
    value_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fir_filed = models.BooleanField(default=False)
    
    # Additional attributes
    description = models.TextField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('reported', 'Reported'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], default='reported')
    
    # File uploads
    fir_document = models.FileField(
        upload_to='fir_documents/%Y/%m/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    item_image = models.ImageField(
        upload_to='item_images/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reported_by = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_incidents')

    class Meta:
        db_table = 'incident_fact'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['occurred_at']),
            models.Index(fields=['location', 'occurred_at']),
            models.Index(fields=['incident_type', 'occurred_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.incident_type.category} at {self.location} on {self.occurred_at.date()}"


class IMEIRegistry(models.Model):
    """Registry for stolen phone IMEIs with tracking"""
    imei = models.CharField(max_length=20, unique=True, db_index=True)
    phone_brand = models.CharField(max_length=100, blank=True)
    phone_model = models.CharField(max_length=100, blank=True)
    owner_name = models.CharField(max_length=150, blank=True)
    owner_contact = models.CharField(max_length=20, blank=True)
    
    # Link to incident if reported through the system
    incident = models.ForeignKey(IncidentFact, on_delete=models.SET_NULL, null=True, blank=True, related_name='imei_records')
    
    status = models.CharField(max_length=20, choices=[
        ('stolen', 'Stolen'),
        ('recovered', 'Recovered'),
        ('flagged', 'Flagged')
    ], default='stolen')
    
    reported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reported_by = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name='imei_reports')
    
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'imei_registry'
        ordering = ['-reported_at']
        verbose_name_plural = 'IMEI Registries'

    def __str__(self):
        return f"{self.imei} - {self.status}"


class AreaAlert(models.Model):
    """Location-based alerts for high-crime areas"""
    location = models.ForeignKey("core.LocationDim", on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=50, choices=[
        ('high_crime', 'High Crime Rate'),
        ('recent_incident', 'Recent Incident'),
        ('warning', 'Warning')
    ])
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], default='medium')
    
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'area_alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.alert_type} - {self.location}"
