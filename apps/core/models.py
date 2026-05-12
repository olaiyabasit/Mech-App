from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """Extended user profile for WInki system"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='winki_profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


class SystemSettings(models.Model):
    """System-wide settings for WInki"""
    
    # Business information
    business_name = models.CharField(max_length=100, default="WInki Refurbishment")
    business_address = models.TextField(blank=True)
    business_phone = models.CharField(max_length=20, blank=True)
    business_email = models.EmailField(blank=True)
    
    # System preferences  
    default_job_duration_days = models.PositiveIntegerField(default=7)
    require_deposit = models.BooleanField(default=True)
    minimum_deposit_percent = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    
    # Notification settings
    send_job_reminders = models.BooleanField(default=True)
    reminder_days_before = models.PositiveIntegerField(default=1)
    
    # QR code settings
    qr_code_prefix = models.CharField(max_length=10, default="WINKI")
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return f"WInki System Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings object exists
        if not self.pk and SystemSettings.objects.exists():
            raise ValueError("Only one SystemSettings instance is allowed.")
        super().save(*args, **kwargs)


class ActivityLog(models.Model):
    """Log of important system activities"""
    
    ACTION_CHOICES = [
        ('job_created', 'Job Created'),
        ('job_updated', 'Job Updated'),
        ('job_completed', 'Job Completed'), 
        ('job_delivered', 'Job Delivered'),
        ('payment_received', 'Payment Received'),
        ('customer_created', 'Customer Created'),
        ('customer_updated', 'Customer Updated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Optional reference to related objects
    object_id = models.CharField(max_length=50, blank=True, help_text="ID of related object")
    object_type = models.CharField(max_length=20, blank=True, help_text="Type of related object")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
    
    def __str__(self):
        user_name = self.user.username if self.user else "System"
        return f"{user_name}: {self.get_action_display()}"
