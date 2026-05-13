from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from apps.jobs.models import Job
from apps.customers.models import Customer
from apps.payments.models import Payment


def home(request):
    """WInki homepage with system overview"""
    context = {
        'page_title': 'Welcome to WInki',
    }
    
    # Add basic statistics if user is authenticated
    if request.user.is_authenticated:
        today = timezone.now().date()
        
        # Basic stats
        context.update({
            'total_customers': Customer.objects.count(),
            'total_jobs': Job.objects.count(),
            'jobs_today': Job.objects.filter(created_date__date=today).count(),
            'pending_jobs': Job.objects.filter(status='pending').count(),
            'in_progress_jobs': Job.objects.filter(status='in_progress').count(),
            'completed_jobs': Job.objects.filter(status='completed').count(),
            'recent_jobs': Job.objects.select_related('customer').order_by('-created_date')[:5],
        })
    
    return render(request, 'base.html', context)


@login_required
def dashboard(request):
    """Main dashboard view"""
    today = timezone.now().date()
    this_month = timezone.now().replace(day=1).date()
    
    # Job statistics
    job_stats = {
        'total': Job.objects.count(),
        'pending': Job.objects.filter(status='pending').count(),
        'in_progress': Job.objects.filter(status='in_progress').count(),
        'completed': Job.objects.filter(status='completed').count(),
        'delivered': Job.objects.filter(status='delivered').count(),
        'today': Job.objects.filter(created_date__date=today).count(),
        'this_month': Job.objects.filter(created_date__date__gte=this_month).count(),
    }
    
    # Financial statistics
    total_revenue = Job.objects.filter(status='delivered').aggregate(
        total=Sum('total_cost'))['total'] or 0
    
    monthly_revenue = Job.objects.filter(
        status='delivered',
        delivered_date__date__gte=this_month
    ).aggregate(total=Sum('total_cost'))['total'] or 0
    
    outstanding_balance = sum(job.outstanding_balance for job in Job.objects.filter(
        status__in=['pending', 'in_progress', 'completed']))
    
    total_jobs_count = job_stats['total']
    average_job_value = round(total_revenue / total_jobs_count, 2) if total_jobs_count else 0
    
    # Recent activity
    recent_jobs = Job.objects.select_related('customer').order_by('-created_date')[:10]
    recent_payments = Payment.objects.select_related('job__customer').order_by('-payment_date')[:5]
    
    context = {
        'job_stats': job_stats,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'outstanding_balance': outstanding_balance,
        'average_job_value': average_job_value,
        'recent_jobs': recent_jobs,
        'recent_payments': recent_payments,
        'total_customers': Customer.objects.count(),
        'current_time': timezone.now(),
    }
    
    return render(request, 'core/dashboard.html', context)
