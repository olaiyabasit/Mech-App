from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Job, VehicleDetails, AlloyWheelDetails, Service, JobPhoto


class VehicleDetailsInline(admin.StackedInline):
    model = VehicleDetails
    extra = 0


class AlloyWheelDetailsInline(admin.StackedInline):
    model = AlloyWheelDetails
    extra = 0


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1


class JobPhotoInline(admin.TabularInline):
    model = JobPhoto
    extra = 1


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'customer', 'job_type', 'status', 'total_cost', 'outstanding_balance', 'created_date']
    list_filter = ['status', 'job_type', 'created_date', 'expected_completion']
    search_fields = ['job_id', 'customer__name', 'description', 'vehicle__plate_number']
    readonly_fields = ['job_id', 'qr_code', 'qr_code_display', 'outstanding_balance', 'total_paid', 'days_since_created', 'is_overdue']
    date_hierarchy = 'created_date'
    
    fieldsets = (
        ('Job Information', {
            'fields': ('job_id', 'customer', 'job_type', 'status')
        }),
        ('Work Details', {
            'fields': ('description', 'internal_notes')
        }),
        ('Financial', {
            'fields': ('total_cost', 'deposit_amount', 'outstanding_balance', 'total_paid')
        }),
        ('Timeline', {
            'fields': ('expected_completion', 'completed_date', 'delivered_date', 'days_since_created', 'is_overdue')
        }),
        ('QR Code & Tracking', {
            'fields': ('qr_code', 'qr_code_display'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [VehicleDetailsInline, AlloyWheelDetailsInline, ServiceInline, JobPhotoInline]
    
    def outstanding_balance(self, obj):
        return f"${obj.outstanding_balance:.2f}"
    outstanding_balance.short_description = 'Outstanding'
    
    def qr_code_display(self, obj):
        if obj.job_id:
            qr_image_url = reverse('jobs:qr_image', args=[obj.job_id])
            qr_lookup_url = reverse('jobs:qr_lookup', args=[obj.qr_code])
            return format_html(
                '''
                <div style="text-align: center;">
                    <p><a href="{}" target="_blank" style="background: #007cba; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;">
                        📱 Download QR Code
                    </a></p>
                    <p><small>QR Code URL: <a href="{}" target="_blank">{}</a></small></p>
                    <p><small>Use this QR code for quick job lookup and customer status checking.</small></p>
                </div>
                ''',
                qr_image_url, qr_lookup_url, qr_lookup_url
            )
        return "Save job first to generate QR code"
    qr_code_display.short_description = 'QR Code'
    qr_code_display.allow_tags = True
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj and obj.status in ['completed', 'delivered']:
            readonly.extend(['total_cost', 'deposit_amount'])
        return readonly


@admin.register(VehicleDetails)
class VehicleDetailsAdmin(admin.ModelAdmin):
    list_display = ['job', 'make', 'model', 'year', 'plate_number', 'color']
    list_filter = ['make', 'year']
    search_fields = ['make', 'model', 'plate_number', 'vin_number']


@admin.register(AlloyWheelDetails)
class AlloyWheelDetailsAdmin(admin.ModelAdmin):
    list_display = ['job', 'wheel_size', 'brand', 'quantity', 'finish_type']
    list_filter = ['wheel_size', 'brand']
    search_fields = ['brand', 'model', 'finish_type']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['job', 'service_name', 'status', 'cost', 'estimated_hours', 'actual_hours']
    list_filter = ['status']
    search_fields = ['service_name', 'job__job_id', 'job__customer__name']


@admin.register(JobPhoto)
class JobPhotoAdmin(admin.ModelAdmin):
    list_display = ['job', 'photo_type', 'caption', 'uploaded_at']
    list_filter = ['photo_type', 'uploaded_at']
    readonly_fields = ['uploaded_at']
