from django.contrib import admin
from .models import IncidentFact, IMEIRegistry, AreaAlert


@admin.register(IncidentFact)
class IncidentFactAdmin(admin.ModelAdmin):
    list_display = ['id', 'incident_type', 'occurred_at', 'location', 'status', 'fir_filed', 'is_anonymous', 'created_at']
    list_filter = ['status', 'fir_filed', 'is_anonymous', 'occurred_at', 'created_at']
    search_fields = ['description', 'location__city', 'location__district']
    date_hierarchy = 'occurred_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Incident Information', {
            'fields': ('incident_type', 'occurred_at', 'description', 'status')
        }),
        ('Location & Victim', {
            'fields': ('location', 'victim', 'is_anonymous')
        }),
        ('Stolen Item', {
            'fields': ('stolen_item', 'value_estimate')
        }),
        ('FIR & Documents', {
            'fields': ('fir_filed', 'fir_document', 'item_image')
        }),
        ('Metadata', {
            'fields': ('reported_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IMEIRegistry)
class IMEIRegistryAdmin(admin.ModelAdmin):
    list_display = ['id', 'imei', 'phone_brand', 'phone_model', 'status', 'owner_name', 'reported_at']
    list_filter = ['status', 'reported_at']
    search_fields = ['imei', 'phone_brand', 'phone_model', 'owner_name', 'owner_contact']
    readonly_fields = ['reported_at', 'updated_at']


@admin.register(AreaAlert)
class AreaAlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'alert_type', 'severity', 'is_active', 'valid_from', 'valid_until']
    list_filter = ['alert_type', 'severity', 'is_active', 'created_at']
    search_fields = ['message', 'location__city', 'location__district']
    readonly_fields = ['created_at']
