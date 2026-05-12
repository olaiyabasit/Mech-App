from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'name', 'phone', 'email', 'city', 'total_jobs', 'total_spent', 'created_at']
    list_filter = ['is_active', 'city', 'created_at']
    search_fields = ['name', 'phone', 'email', 'address']
    readonly_fields = ['customer_id', 'created_at', 'updated_at', 'total_jobs', 'total_spent', 'outstanding_balance']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_id', 'name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address', 'city', 'postal_code')
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active')
        }),
        ('Statistics', {
            'fields': ('total_jobs', 'total_spent', 'outstanding_balance'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_jobs(self, obj):
        return obj.total_jobs
    total_jobs.short_description = 'Total Jobs'
    
    def total_spent(self, obj):
        return f"${obj.total_spent:.2f}"
    total_spent.short_description = 'Total Spent'
