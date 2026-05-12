from django.db import models
from django.urls import reverse


class Customer(models.Model):
    """Customer model for WInki refurbishment bookkeeping system"""
    
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True, help_text="Customer's full name")
    email = models.EmailField(blank=True, null=True, db_index=True, help_text="Customer's email address")
    phone = models.CharField(max_length=20, db_index=True, help_text="Primary phone number")
    address = models.TextField(blank=True, help_text="Full address")
    city = models.CharField(max_length=50, blank=True, help_text="City")
    postal_code = models.CharField(max_length=10, blank=True, help_text="Postal/ZIP code")
    notes = models.TextField(blank=True, help_text="Internal notes about customer")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Whether customer is active")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'created_at']),
            models.Index(fields=['phone', 'email']),
        ]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
    
    def __str__(self):
        return f"{self.name} (ID: {self.customer_id})"
    
    def get_absolute_url(self):
        return reverse('customers:detail', kwargs={'pk': self.customer_id})
    
    @property
    def total_jobs(self):
        """Return total number of jobs for this customer"""
        return self.jobs.count()
    
    @property
    def total_spent(self):
        """Return total amount spent by this customer"""
        return sum(job.total_cost for job in self.jobs.all())
    
    @property
    def outstanding_balance(self):
        """Return total outstanding balance across all jobs"""
        return sum(job.outstanding_balance for job in self.jobs.filter(
            status__in=['pending', 'in_progress', 'completed']
        ))
