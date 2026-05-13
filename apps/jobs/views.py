from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from .models import Job, VehicleDetails, AlloyWheelDetails, Service
from apps.customers.models import Customer


@login_required
def job_list(request):
    jobs = Job.objects.select_related('customer').prefetch_related('payments')
    q = request.GET.get('q', '').strip()
    if q:
        jobs = jobs.filter(
            Q(job_id__icontains=q)|Q(customer__name__icontains=q)|
            Q(customer__phone__icontains=q)|Q(description__icontains=q)
        )
    status = request.GET.get('status', '')
    if status:
        jobs = jobs.filter(status=status)
    job_type = request.GET.get('type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    return render(request, 'jobs/job_list.html', {
        'jobs': jobs, 'q': q, 'status_filter': status, 'type_filter': job_type,
        'status_choices': Job.JOB_STATUS_CHOICES, 'type_choices': Job.JOB_TYPE_CHOICES,
        'total': jobs.count(),
    })


@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related('customer').prefetch_related('payments','services','photos'), pk=pk)
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'payments': job.payments.all(),
        'services': job.services.all(),
        'vehicle': getattr(job, 'vehicle', None),
        'alloy': getattr(job, 'alloy_wheels', None),
    })


@login_required
def job_create(request):
    customers = Customer.objects.filter(is_active=True).order_by('name')
    if request.method == 'POST':
        p = request.POST
        try:
            job = Job(
                customer=get_object_or_404(Customer, pk=p['customer']),
                job_type=p['job_type'],
                status=p.get('status','pending'),
                total_cost=p.get('total_cost') or 0,
                deposit_amount=p.get('deposit_amount') or 0,
                description=p.get('description',''),
                internal_notes=p.get('internal_notes',''),
                expected_completion=p.get('expected_completion') or None,
            )
            job.save()
            if job.job_type in ('vehicle','both') and p.get('vehicle_make'):
                VehicleDetails.objects.create(job=job, make=p.get('vehicle_make',''), model=p.get('vehicle_model',''),
                    year=p.get('vehicle_year') or 2000, plate_number=p.get('plate_number',''),
                    color=p.get('vehicle_color',''), mileage=p.get('mileage') or None, vin_number=p.get('vin_number',''))
            if job.job_type in ('alloy','both') and p.get('wheel_size'):
                AlloyWheelDetails.objects.create(job=job, wheel_size=p.get('wheel_size',''),
                    brand=p.get('wheel_brand',''), model=p.get('wheel_model_alloy',''),
                    quantity=p.get('wheel_quantity') or 4, damage_description=p.get('damage_description',''),
                    finish_type=p.get('finish_type',''))
            messages.success(request, f'Job {job.job_id} created successfully.')
            return redirect('jobs:detail', pk=job.job_id)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'jobs/job_form.html', {
        'customers': customers, 'status_choices': Job.JOB_STATUS_CHOICES,
        'type_choices': Job.JOB_TYPE_CHOICES, 'action': 'Create',
    })


@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    customers = Customer.objects.filter(is_active=True).order_by('name')
    vehicle = getattr(job, 'vehicle', None)
    alloy = getattr(job, 'alloy_wheels', None)
    if request.method == 'POST':
        p = request.POST
        try:
            job.customer = get_object_or_404(Customer, pk=p['customer'])
            job.job_type = p['job_type']
            job.status = p['status']
            job.total_cost = p.get('total_cost') or 0
            job.deposit_amount = p.get('deposit_amount') or 0
            job.description = p.get('description','')
            job.internal_notes = p.get('internal_notes','')
            job.expected_completion = p.get('expected_completion') or None
            if job.status == 'completed' and not job.completed_date:
                job.completed_date = timezone.now()
            if job.status == 'delivered' and not job.delivered_date:
                job.delivered_date = timezone.now()
            job.save()
            if job.job_type in ('vehicle','both') and p.get('vehicle_make'):
                VehicleDetails.objects.update_or_create(job=job, defaults=dict(
                    make=p.get('vehicle_make',''), model=p.get('vehicle_model',''),
                    year=p.get('vehicle_year') or 2000, plate_number=p.get('plate_number',''),
                    color=p.get('vehicle_color',''), mileage=p.get('mileage') or None, vin_number=p.get('vin_number','')))
            if job.job_type in ('alloy','both') and p.get('wheel_size'):
                AlloyWheelDetails.objects.update_or_create(job=job, defaults=dict(
                    wheel_size=p.get('wheel_size',''), brand=p.get('wheel_brand',''),
                    model=p.get('wheel_model_alloy',''), quantity=p.get('wheel_quantity') or 4,
                    damage_description=p.get('damage_description',''), finish_type=p.get('finish_type','')))
            messages.success(request, f'Job {job.job_id} updated.')
            return redirect('jobs:detail', pk=job.job_id)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'jobs/job_form.html', {
        'job': job, 'vehicle': vehicle, 'alloy': alloy, 'customers': customers,
        'status_choices': Job.JOB_STATUS_CHOICES, 'type_choices': Job.JOB_TYPE_CHOICES, 'action': 'Edit',
    })


@login_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        jid = job.job_id; job.delete()
        messages.success(request, f'Job {jid} deleted.')
        return redirect('jobs:list')
    return render(request, 'jobs/job_confirm_delete.html', {'job': job})


@login_required
def job_update_status(request, pk):
    if request.method == 'POST':
        job = get_object_or_404(Job, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Job.JOB_STATUS_CHOICES):
            job.status = new_status
            if new_status == 'completed' and not job.completed_date:
                job.completed_date = timezone.now()
            if new_status == 'delivered' and not job.delivered_date:
                job.delivered_date = timezone.now()
            job.save()
            messages.success(request, f'Status updated to {job.get_status_display()}.')
    return redirect('jobs:detail', pk=pk)


def qr_code_lookup(request, qr_code):
    job = get_object_or_404(Job, qr_code=qr_code)
    return render(request, 'jobs/qr_lookup.html', {'job': job})


def job_status_api(request, qr_code):
    job = get_object_or_404(Job, qr_code=qr_code)
    return JsonResponse({'job_id': job.job_id, 'status': job.status,
        'status_display': job.get_status_display(), 'customer': job.customer.name,
        'total_cost': str(job.total_cost), 'outstanding': str(job.outstanding_balance)})


def generate_qr_code_image(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    buffer = job.generate_qr_code_image()
    return HttpResponse(buffer.getvalue(), content_type='image/png')
