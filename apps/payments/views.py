from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from .models import Payment
from apps.jobs.models import Job


@login_required
def payment_list(request):
    payments = Payment.objects.select_related('job__customer').order_by('-payment_date')
    q = request.GET.get('q', '').strip()
    if q:
        payments = payments.filter(Q(job__job_id__icontains=q)|Q(job__customer__name__icontains=q)|Q(reference_number__icontains=q))
    method = request.GET.get('method', '')
    if method:
        payments = payments.filter(payment_method=method)
    ptype = request.GET.get('type', '')
    if ptype:
        payments = payments.filter(payment_type=ptype)
    total_amount = payments.aggregate(t=Sum('amount'))['t'] or 0
    return render(request, 'payments/payment_list.html', {
        'payments': payments, 'q': q, 'method_filter': method, 'type_filter': ptype,
        'method_choices': Payment.PAYMENT_METHOD_CHOICES, 'type_choices': Payment.PAYMENT_TYPE_CHOICES,
        'total_amount': total_amount, 'total': payments.count(),
    })


@login_required
def payment_create(request):
    job_id = request.GET.get('job', '')
    jobs = Job.objects.select_related('customer').order_by('-created_date')
    preselected_job = None
    if job_id:
        preselected_job = Job.objects.filter(pk=job_id).first()

    if request.method == 'POST':
        p = request.POST
        try:
            job = get_object_or_404(Job, pk=p['job'])
            Payment.objects.create(
                job=job,
                amount=p['amount'],
                payment_method=p['payment_method'],
                payment_type=p['payment_type'],
                payment_date=p.get('payment_date') or timezone.now(),
                reference_number=p.get('reference_number',''),
                notes=p.get('notes',''),
                created_by=request.user,
            )
            messages.success(request, 'Payment recorded successfully.')
            return redirect('jobs:detail', pk=job.job_id)
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return render(request, 'payments/payment_form.html', {
        'jobs': jobs, 'preselected_job': preselected_job,
        'method_choices': Payment.PAYMENT_METHOD_CHOICES,
        'type_choices': Payment.PAYMENT_TYPE_CHOICES,
        'action': 'Record',
    })


@login_required
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    jobs = Job.objects.select_related('customer').order_by('-created_date')
    if request.method == 'POST':
        p = request.POST
        try:
            payment.job = get_object_or_404(Job, pk=p['job'])
            payment.amount = p['amount']
            payment.payment_method = p['payment_method']
            payment.payment_type = p['payment_type']
            payment.payment_date = p.get('payment_date') or payment.payment_date
            payment.reference_number = p.get('reference_number','')
            payment.notes = p.get('notes','')
            payment.save()
            messages.success(request, 'Payment updated.')
            return redirect('jobs:detail', pk=payment.job.job_id)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'payments/payment_form.html', {
        'payment': payment, 'jobs': jobs,
        'method_choices': Payment.PAYMENT_METHOD_CHOICES,
        'type_choices': Payment.PAYMENT_TYPE_CHOICES,
        'action': 'Edit',
    })


@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        job_id = payment.job.job_id
        payment.delete()
        messages.success(request, 'Payment deleted.')
        return redirect('jobs:detail', pk=job_id)
    return render(request, 'payments/payment_confirm_delete.html', {'payment': payment})
