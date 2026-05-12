from django.contrib import admin
from .models import UserProfile, SystemSettings, ActivityLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'email_notifications', 'last_active']
    list_filter = ['role', 'email_notifications', 'sms_notifications']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'last_active']


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Business Information', {
            'fields': ('business_name', 'business_address', 'business_phone', 'business_email')
        }),
        ('System Preferences', {
            'fields': ('default_job_duration_days', 'require_deposit', 'minimum_deposit_percent')
        }),
        ('Notification Settings', {
            'fields': ('send_job_reminders', 'reminder_days_before')
        }),
        ('QR Code Settings', {
            'fields': ('qr_code_prefix',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one SystemSettings instance
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of SystemSettings
        return False


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'description', 'object_type', 'object_id']
    list_filter = ['action', 'timestamp', 'object_type']
    search_fields = ['description', 'object_id', 'user__username']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        # Activity logs are created automatically
        return False
