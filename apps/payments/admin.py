from django.contrib import admin
from .models import Payment, PaymentReminder


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'job', 'customer_name', 'amount', 'payment_type', 'payment_method', 'payment_date']
    list_filter = ['payment_type', 'payment_method', 'payment_date']
    search_fields = ['job__job_id', 'job__customer__name', 'reference_number']
    readonly_fields = ['payment_id', 'created_at', 'effective_amount']
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'job', 'amount', 'payment_type', 'payment_method')
        }),
        ('Details', {
            'fields': ('payment_date', 'reference_number', 'notes')
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'effective_amount'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_name(self, obj):
        return obj.job.customer.name
    customer_name.short_description = 'Customer'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new payments
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ['job', 'customer_name', 'reminder_type', 'scheduled_date', 'status', 'sent_date']
    list_filter = ['reminder_type', 'status', 'scheduled_date']
    search_fields = ['job__job_id', 'job__customer__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Reminder Information', {
            'fields': ('job', 'reminder_type', 'scheduled_date', 'status')
        }),
        ('Content', {
            'fields': ('message', 'notes')
        }),
        ('Tracking', {
            'fields': ('sent_date', 'created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_name(self, obj):
        return obj.job.customer.name
    customer_name.short_description = 'Customer'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new reminders
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
