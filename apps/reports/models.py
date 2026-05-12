from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ReportTemplate(models.Model):
    """Saved report templates for recurring reports"""
    
    REPORT_TYPE_CHOICES = [
        ('financial', 'Financial Report'),
        ('operational', 'Operational Report'),
        ('customer', 'Customer Analytics'),
        ('custom', 'Custom Report'),
    ]
    
    name = models.CharField(max_length=100, help_text="Report template name")
    report_type = models.CharField(max_length=15, choices=REPORT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Report configuration (stored as JSON)
    config = models.JSONField(default=dict, help_text="Report configuration parameters")
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True, 
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'), 
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ])
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Report Template"
        verbose_name_plural = "Report Templates"
    
    def __str__(self):
        return self.name


class ReportExecution(models.Model):
    """Log of report executions"""
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, 
                                related_name='executions', blank=True, null=True)
    name = models.CharField(max_length=100, help_text="Report execution name")
    
    # Execution details
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='running')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Parameters
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    parameters = models.JSONField(default=dict, help_text="Report parameters")
    
    # Results
    file_path = models.CharField(max_length=255, blank=True, help_text="Path to generated report file")
    file_format = models.CharField(max_length=10, blank=True, 
        choices=[
            ('pdf', 'PDF'),
            ('excel', 'Excel'),
            ('csv', 'CSV'),
        ])
    
    # Tracking
    executed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    error_message = models.TextField(blank=True, help_text="Error message if failed")
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Report Execution"
        verbose_name_plural = "Report Executions"
    
    def __str__(self):
        return f"{self.name} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def duration(self):
        """Calculate execution duration"""
        if self.completed_at:
            return self.completed_at - self.started_at
        return None
