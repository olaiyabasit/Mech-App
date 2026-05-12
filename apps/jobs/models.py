from django.db import models
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import qrcode
from qrcode import constants
from io import BytesIO
import uuid
import os
from apps.customers.models import Customer


class Job(models.Model):
    """Job model for tracking vehicle and alloy wheel refurbishment work"""
    
    JOB_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('vehicle', 'Vehicle Refurbishment'),
        ('alloy', 'Alloy Wheels'),
        ('both', 'Vehicle & Alloy Wheels'),
    ]
    
    # Primary fields
    job_id = models.CharField(max_length=20, primary_key=True, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='jobs')
    job_type = models.CharField(max_length=10, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=JOB_STATUS_CHOICES, default='pending', db_index=True)
    
    # Financial fields
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Descriptions
    description = models.TextField(help_text="Work to be performed")
    internal_notes = models.TextField(blank=True, help_text="Internal staff notes")
    
    # Dates
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    expected_completion = models.DateField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    delivered_date = models.DateTimeField(blank=True, null=True)
    
    # QR Code and tracking
    qr_code = models.CharField(max_length=100, blank=True, help_text="QR code for quick lookup")
    
    class Meta:
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['status', 'created_date']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['job_type', 'status']),
        ]
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
    
    def save(self, *args, **kwargs):
        if not self.job_id:
            # Generate job ID: WINKI-YYYY-NNNN (e.g., WINKI-2024-0001)
            year = timezone.now().year
            last_job = Job.objects.filter(
                job_id__startswith=f'WINKI-{year}-'
            ).order_by('job_id').last()
            
            if last_job:
                last_number = int(last_job.job_id.split('-')[2])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.job_id = f'WINKI-{year}-{new_number:04d}'
        
        # Generate QR code if not exists
        if not self.qr_code:
            self.qr_code = str(uuid.uuid4())
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.job_id} - {self.customer.name}"
    
    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.job_id})
    
    @property
    def outstanding_balance(self):
        """Calculate outstanding balance"""
        paid_amount = sum(payment.amount for payment in self.payments.all())
        return max(Decimal('0.00'), self.total_cost - paid_amount)
    
    @property 
    def total_paid(self):
        """Calculate total amount paid"""
        return sum(payment.amount for payment in self.payments.all())
    
    @property
    def days_since_created(self):
        """Days since job was created"""
        return (timezone.now().date() - self.created_date.date()).days
    
    @property
    def is_overdue(self):
        """Check if job is overdue based on expected completion"""
        if self.expected_completion and self.status not in ['completed', 'delivered', 'cancelled']:
            return timezone.now().date() > self.expected_completion
        return False
    
    def generate_qr_code_url(self):
        """Generate URL for QR code access"""
        return f"/jobs/qr/{self.qr_code}/"
    
    def generate_qr_code_image(self):
        """Generate QR code image as BytesIO object"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # QR code contains job lookup URL
        base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
        qr_data = f"{base_url}/jobs/qr/{self.qr_code}/"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to BytesIO for storage/response
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer


class VehicleDetails(models.Model):
    """Vehicle details for jobs involving vehicle work"""
    
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='vehicle')
    make = models.CharField(max_length=50, help_text="Vehicle make (e.g., Toyota)")
    model = models.CharField(max_length=50, help_text="Vehicle model (e.g., Camry)")
    year = models.PositiveIntegerField(help_text="Manufacturing year")
    plate_number = models.CharField(max_length=15, db_index=True, help_text="License plate number")
    color = models.CharField(max_length=30, blank=True, help_text="Vehicle color")
    mileage = models.PositiveIntegerField(blank=True, null=True, help_text="Current mileage")
    vin_number = models.CharField(max_length=17, blank=True, help_text="Vehicle Identification Number")
    
    class Meta:
        verbose_name = "Vehicle Details"
        verbose_name_plural = "Vehicle Details"
        indexes = [
            models.Index(fields=['plate_number']),
            models.Index(fields=['make', 'model']),
        ]
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} - {self.plate_number}"


class AlloyWheelDetails(models.Model):
    """Alloy wheel details for jobs involving wheel work"""
    
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='alloy_wheels')
    wheel_size = models.CharField(max_length=10, help_text="Wheel size (e.g., 17x8)")
    brand = models.CharField(max_length=50, blank=True, help_text="Wheel brand")
    model = models.CharField(max_length=50, blank=True, help_text="Wheel model")
    quantity = models.PositiveIntegerField(default=4, help_text="Number of wheels")
    damage_description = models.TextField(help_text="Description of damage/work needed")
    finish_type = models.CharField(max_length=50, blank=True, help_text="Finish type (e.g., Gloss Black)")
    
    class Meta:
        verbose_name = "Alloy Wheel Details"
        verbose_name_plural = "Alloy Wheel Details"
    
    def __str__(self):
        return f"{self.wheel_size} {self.brand} {self.model} (x{self.quantity})"


class Service(models.Model):
    """Individual services performed as part of a job"""
    
    SERVICE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=100, help_text="Name of service")
    description = models.TextField(blank=True, help_text="Service description")
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=15, choices=SERVICE_STATUS_CHOICES, default='pending')
    
    # Time tracking
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    class Meta:
        ordering = ['job', 'service_name']
        verbose_name = "Service"
        verbose_name_plural = "Services"
    
    def __str__(self):
        return f"{self.service_name} - {self.job.job_id}"


class JobPhoto(models.Model):
    """Photos associated with jobs (before, during, after)"""
    
    PHOTO_TYPE_CHOICES = [
        ('before', 'Before'),
        ('progress', 'Work in Progress'),
        ('after', 'After/Completed'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='job_photos/%Y/%m/', help_text="Upload job photo")
    photo_type = models.CharField(max_length=10, choices=PHOTO_TYPE_CHOICES)
    caption = models.CharField(max_length=200, blank=True, help_text="Photo description")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['photo_type', 'uploaded_at']
        verbose_name = "Job Photo"
        verbose_name_plural = "Job Photos"
    
    def __str__(self):
        return f"{self.job.job_id} - {self.get_photo_type_display()}"
