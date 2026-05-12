from django.contrib import admin
from .models import ReportTemplate, ReportExecution


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_scheduled', 'schedule_frequency', 'last_run', 'created_by']
    list_filter = ['report_type', 'is_scheduled', 'schedule_frequency']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'last_run']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'report_type', 'description')
        }),
        ('Configuration', {
            'fields': ('config',)
        }),
        ('Scheduling', {
            'fields': ('is_scheduled', 'schedule_frequency')
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'last_run'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new templates
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'status', 'started_at', 'completed_at', 'duration_display', 'executed_by']
    list_filter = ['status', 'file_format', 'started_at']
    search_fields = ['name', 'template__name']
    readonly_fields = ['started_at', 'completed_at', 'duration_display']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Execution Information', {
            'fields': ('name', 'template', 'status')
        }),
        ('Parameters', {
            'fields': ('date_from', 'date_to', 'parameters')
        }),
        ('Results', {
            'fields': ('file_path', 'file_format', 'error_message')
        }),
        ('Tracking', {
            'fields': ('executed_by', 'started_at', 'completed_at', 'duration_display'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        if obj.duration:
            return str(obj.duration)
        return '-'
    duration_display.short_description = 'Duration'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set executed_by for new executions
            obj.executed_by = request.user
        super().save_model(request, obj, form, change)
