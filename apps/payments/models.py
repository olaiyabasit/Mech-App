from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
from apps.jobs.models import Job


class Payment(models.Model):
    """Payment tracking for jobs"""
    
    PAYMENT_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('partial', 'Partial Payment'),
        ('final', 'Final Payment'),
        ('refund', 'Refund'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('online', 'Online Payment'),
    ]
    
    # Primary fields
    payment_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Payment amount")
    
    # Payment details
    payment_date = models.DateTimeField(default=timezone.now, db_index=True)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    reference_number = models.CharField(max_length=50, blank=True, help_text="Check number, transaction ID, etc.")
    
    # Additional info
    notes = models.TextField(blank=True, help_text="Payment notes")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, help_text="Staff member who recorded payment")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['job', 'payment_date']),
            models.Index(fields=['payment_method', 'payment_date']),
            models.Index(fields=['payment_type', 'payment_date']),
        ]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.job.job_id} - ${self.amount}"
    
    def get_absolute_url(self):
        return reverse('payments:detail', kwargs={'pk': self.payment_id})
    
    @property
    def is_refund(self):
        """Check if this is a refund payment"""
        return self.payment_type == 'refund'
    
    @property
    def effective_amount(self):
        """Return amount considering refunds as negative"""
        return -self.amount if self.is_refund else self.amount


class PaymentReminder(models.Model):
    """Reminders for outstanding payments"""
    
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Phone Call'),
        ('letter', 'Letter'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('responded', 'Customer Responded'),
        ('cancelled', 'Cancelled'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='payment_reminders')
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPE_CHOICES)
    scheduled_date = models.DateTimeField(help_text="When to send reminder")
    sent_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Content
    message = models.TextField(help_text="Reminder message")
    notes = models.TextField(blank=True, help_text="Follow-up notes")
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['scheduled_date']
        verbose_name = "Payment Reminder"
        verbose_name_plural = "Payment Reminders"
    
    def __str__(self):
        return f"Reminder for {self.job.job_id} - {self.get_reminder_type_display()}"
