from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from .models import Customer


@login_required
def customer_list(request):
    customers = Customer.objects.annotate(job_count=Count('jobs'), total_value=Sum('jobs__total_cost'))
    q = request.GET.get('q', '').strip()
    if q:
        customers = customers.filter(Q(name__icontains=q)|Q(phone__icontains=q)|Q(email__icontains=q)|Q(city__icontains=q))
    active = request.GET.get('active', '')
    if active == '1':
        customers = customers.filter(is_active=True)
    elif active == '0':
        customers = customers.filter(is_active=False)
    return render(request, 'customers/customer_list.html', {
        'customers': customers, 'q': q, 'active_filter': active, 'total': customers.count(),
    })


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    jobs = customer.jobs.prefetch_related('payments').order_by('-created_date')
    return render(request, 'customers/customer_detail.html', {
        'customer': customer, 'jobs': jobs,
    })


@login_required
def customer_create(request):
    if request.method == 'POST':
        p = request.POST
        try:
            c = Customer.objects.create(
                name=p['name'], email=p.get('email') or None,
                phone=p.get('phone',''), address=p.get('address',''),
                city=p.get('city',''), postal_code=p.get('postal_code',''),
                notes=p.get('notes',''), is_active=p.get('is_active')=='on',
            )
            messages.success(request, f'Customer {c.name} created.')
            return redirect('customers:detail', pk=c.pk)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'customers/customer_form.html', {'action': 'Create'})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        p = request.POST
        try:
            customer.name = p['name']
            customer.email = p.get('email') or None
            customer.phone = p.get('phone','')
            customer.address = p.get('address','')
            customer.city = p.get('city','')
            customer.postal_code = p.get('postal_code','')
            customer.notes = p.get('notes','')
            customer.is_active = p.get('is_active') == 'on'
            customer.save()
            messages.success(request, f'Customer {customer.name} updated.')
            return redirect('customers:detail', pk=customer.pk)
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'customers/customer_form.html', {'customer': customer, 'action': 'Edit'})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        name = customer.name
        try:
            customer.delete()
            messages.success(request, f'Customer {name} deleted.')
            return redirect('customers:list')
        except Exception as e:
            messages.error(request, f'Cannot delete: {e}')
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})
