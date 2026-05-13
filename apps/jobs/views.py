from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Job


def qr_code_lookup(request, qr_code):
    """Handle QR code lookup and redirect to job details"""
    job = get_object_or_404(Job, qr_code=qr_code)
    
    # If it's an API request, return JSON
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'job_id': job.job_id,
            'customer': job.customer.name,
            'status': job.get_status_display(),
            'total_cost': float(job.total_cost),
            'outstanding_balance': float(job.outstanding_balance),
            'created_date': job.created_date.isoformat(),
        })
    
    # Otherwise redirect to admin page
    return redirect(f'/admin/jobs/job/{job.job_id}/change/')


def generate_qr_code_image(request, job_id):
    """Generate and return QR code image for a job"""
    job = get_object_or_404(Job, job_id=job_id)
    
    # Generate QR code image
    qr_image = job.generate_qr_code_image()
    
    # Return as PNG response
    response = HttpResponse(qr_image, content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="{job.job_id}_qr_code.png"'
    return response


def job_status_api(request, qr_code):
    """API endpoint for mobile apps to check job status via QR code"""
    job = get_object_or_404(Job, qr_code=qr_code)
    
    return JsonResponse({
        'success': True,
        'job': {
            'job_id': job.job_id,
            'customer_name': job.customer.name,
            'customer_phone': job.customer.phone,
            'job_type': job.get_job_type_display(),
            'status': job.get_status_display(),
            'description': job.description,
            'total_cost': float(job.total_cost),
            'total_paid': float(job.total_paid),
            'outstanding_balance': float(job.outstanding_balance),
            'created_date': job.created_date.strftime('%Y-%m-%d'),
            'expected_completion': job.expected_completion.strftime('%Y-%m-%d') if job.expected_completion else None,
            'completed_date': job.completed_date.strftime('%Y-%m-%d %H:%M') if job.completed_date else None,
            'is_overdue': job.is_overdue,
            'days_since_created': job.days_since_created,
        }
    })
