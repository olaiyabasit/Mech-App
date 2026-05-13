from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import Job
from apps.customers.models import Customer
from apps.payments.models import Payment


def home(request):
    """WInki homepage with system overview"""
    context = {
        'page_title': 'Welcome to WInki',
    }
    if request.user.is_authenticated:
        today = timezone.now().date()
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
    this_month_start = timezone.now().replace(day=1).date()
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)

    # ── Job statistics ──
    job_stats = {
        'total': Job.objects.count(),
        'pending': Job.objects.filter(status='pending').count(),
        'in_progress': Job.objects.filter(status='in_progress').count(),
        'completed': Job.objects.filter(status='completed').count(),
        'delivered': Job.objects.filter(status='delivered').count(),
        'cancelled': Job.objects.filter(status='cancelled').count(),
        'today': Job.objects.filter(created_date__date=today).count(),
        'this_month': Job.objects.filter(created_date__date__gte=this_month_start).count(),
        'last_7_days': Job.objects.filter(created_date__date__gte=last_7_days).count(),
        'overdue': sum(1 for j in Job.objects.filter(
            status__in=['pending', 'in_progress'],
            expected_completion__lt=today
        ).only('expected_completion', 'status')),
    }

    # ── Financial statistics ──
    total_revenue = Job.objects.filter(status='delivered').aggregate(
        total=Sum('total_cost'))['total'] or 0

    monthly_revenue = Job.objects.filter(
        status='delivered',
        delivered_date__date__gte=this_month_start
    ).aggregate(total=Sum('total_cost'))['total'] or 0

    last_month_revenue = Job.objects.filter(
        status='delivered',
        delivered_date__date__gte=last_month_start,
        delivered_date__date__lte=last_month_end,
    ).aggregate(total=Sum('total_cost'))['total'] or 0

    # Month-over-month growth
    if last_month_revenue > 0:
        revenue_growth = round(((monthly_revenue - last_month_revenue) / last_month_revenue) * 100, 1)
    else:
        revenue_growth = 0

    outstanding_balance = sum(
        job.outstanding_balance for job in Job.objects.filter(
            status__in=['pending', 'in_progress', 'completed']
        ).prefetch_related('payments')
    )

    total_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_jobs_count = job_stats['total']
    average_job_value = round(float(total_revenue) / total_jobs_count, 2) if total_jobs_count else 0

    # Collection rate
    total_invoiced = float(total_revenue) + float(outstanding_balance)
    collection_rate = round((float(total_revenue) / total_invoiced * 100), 1) if total_invoiced > 0 else 0

    # ── Recent payments totals ──
    payments_this_month = Payment.objects.filter(
        payment_date__date__gte=this_month_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    payments_today = Payment.objects.filter(
        payment_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    # ── Job type breakdown ──
    job_type_stats = list(Job.objects.values('job_type').annotate(count=Count('job_id')))

    # ── Recent activity ──
    recent_jobs = Job.objects.select_related('customer').order_by('-created_date')[:10]
    recent_payments = Payment.objects.select_related('job__customer').order_by('-payment_date')[:8]

    # ── Top customers ──
    top_customers = Customer.objects.annotate(
        job_count=Count('jobs'),
        total_value=Sum('jobs__total_cost')
    ).filter(job_count__gt=0).order_by('-total_value')[:5]

    # ── Overdue jobs ──
    overdue_jobs = Job.objects.filter(
        status__in=['pending', 'in_progress'],
        expected_completion__lt=today
    ).select_related('customer').order_by('expected_completion')[:5]

    # ── Activity per day last 7 days for sparkline ──
    daily_jobs = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        count = Job.objects.filter(created_date__date=d).count()
        daily_jobs.append({'date': d.strftime('%a'), 'count': count})

    context = {
        'job_stats': job_stats,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'last_month_revenue': last_month_revenue,
        'revenue_growth': revenue_growth,
        'outstanding_balance': outstanding_balance,
        'total_payments': total_payments,
        'payments_this_month': payments_this_month,
        'payments_today': payments_today,
        'average_job_value': average_job_value,
        'collection_rate': collection_rate,
        'recent_jobs': recent_jobs,
        'recent_payments': recent_payments,
        'top_customers': top_customers,
        'overdue_jobs': overdue_jobs,
        'total_customers': Customer.objects.count(),
        'new_customers_month': Customer.objects.filter(created_at__date__gte=this_month_start).count(),
        'job_type_stats': job_type_stats,
        'daily_jobs': daily_jobs,
        'current_time': timezone.now(),
    }

    return render(request, 'core/dashboard.html', context)
