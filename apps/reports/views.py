from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
import csv
from decimal import Decimal
from apps.jobs.models import Job
from apps.customers.models import Customer
from apps.payments.models import Payment


def jobs_report_pdf(request):
    """Generate PDF report for jobs"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="winki_jobs_report.pdf"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("WInki Jobs Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Report info
    report_date = timezone.now().strftime('%B %d, %Y at %I:%M %p')
    info = Paragraph(f"Generated on: {report_date}", styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 12))
    
    # Jobs data
    jobs = Job.objects.all().order_by('-created_date')
    
    # Summary statistics
    total_jobs = jobs.count()
    completed_jobs = jobs.filter(status='completed').count()
    pending_jobs = jobs.filter(status='pending').count()
    total_revenue = sum(job.total_cost for job in jobs)
    
    summary_text = f"""
    Summary:
    • Total Jobs: {total_jobs}
    • Completed Jobs: {completed_jobs}
    • Pending Jobs: {pending_jobs}
    • Total Revenue: ${total_revenue:,.2f}
    """
    summary = Paragraph(summary_text, styles['Normal'])
    elements.append(summary)
    elements.append(Spacer(1, 20))
    
    # Jobs table
    table_data = [['Job ID', 'Customer', 'Type', 'Status', 'Cost', 'Outstanding']]
    
    for job in jobs[:20]:  # Limit to first 20 jobs
        table_data.append([
            job.job_id,
            job.customer.name[:20],  # Truncate long names
            job.get_job_type_display(),
            job.get_status_display(),
            f"${job.total_cost}",
            f"${job.outstanding_balance}"
        ])
    
    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    return response


def customers_export_csv(request):
    """Export customers to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="winki_customers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Address', 'Jobs Count', 'Total Spent'])
    
    customers = Customer.objects.all()
    for customer in customers:
        jobs_count = customer.jobs.count()
        total_spent = sum(job.total_cost for job in customer.jobs.all())
        
        writer.writerow([
            customer.name,
            customer.email or '',
            customer.phone or '',
            customer.address or '',
            jobs_count,
            f"${total_spent:.2f}"
        ])
    
    return response


def financial_report_pdf(request):
    """Generate financial summary PDF"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="winki_financial_report.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("WInki Financial Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Report date
    report_date = timezone.now().strftime('%B %d, %Y')
    date_para = Paragraph(f"Report Date: {report_date}", styles['Normal'])
    elements.append(date_para)
    elements.append(Spacer(1, 20))
    
    # Financial calculations
    jobs = Job.objects.all()
    payments = Payment.objects.all()
    
    total_revenue = sum(job.total_cost for job in jobs)
    total_collected = sum(payment.amount for payment in payments)
    outstanding_balance = total_revenue - total_collected
    
    completed_revenue = sum(job.total_cost for job in jobs.filter(status='completed'))
    pending_revenue = sum(job.total_cost for job in jobs.filter(status='pending'))
    
    # Financial summary table
    financial_data = [
        ['Metric', 'Amount'],
        ['Total Revenue (All Jobs)', f'${total_revenue:,.2f}'],
        ['Total Collected', f'${total_collected:,.2f}'],
        ['Outstanding Balance', f'${outstanding_balance:,.2f}'],
        ['Completed Jobs Revenue', f'${completed_revenue:,.2f}'],
        ['Pending Jobs Value', f'${pending_revenue:,.2f}'],
        ['Collection Rate', f'{(total_collected/total_revenue*100):.1f}%' if total_revenue > 0 else '0%']
    ]
    
    financial_table = Table(financial_data, colWidths=[3*inch, 2*inch])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(financial_table)
    elements.append(Spacer(1, 20))
    
    # Recent payments table
    recent_payments = Payment.objects.order_by('-payment_date')[:10]
    
    payments_para = Paragraph("Recent Payments (Last 10)", styles['Heading2'])
    elements.append(payments_para)
    elements.append(Spacer(1, 12))
    
    payment_data = [['Date', 'Job ID', 'Customer', 'Amount', 'Method']]
    
    for payment in recent_payments:
        payment_data.append([
            payment.payment_date.strftime('%m/%d/%Y'),
            payment.job.job_id,
            payment.job.customer.name[:15],
            f'${payment.amount}',
            payment.get_payment_method_display()
        ])
    
    payments_table = Table(payment_data)
    payments_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(payments_table)
    
    # Build PDF
    doc.build(elements)
    return response


def reports_dashboard(request):
    """Reports dashboard view"""
    # Calculate key metrics for dashboard
    total_jobs = Job.objects.count()
    total_customers = Customer.objects.count()
    total_payments = Payment.objects.count()
    
    total_revenue = sum(job.total_cost for job in Job.objects.all())
    total_collected = sum(payment.amount for payment in Payment.objects.all())
    outstanding_balance = total_revenue - total_collected
    
    context = {
        'total_jobs': total_jobs,
        'total_customers': total_customers,
        'total_payments': total_payments,
        'total_revenue': total_revenue,
        'total_collected': total_collected,
        'outstanding_balance': outstanding_balance,
        'collection_rate': (total_collected / total_revenue * 100) if total_revenue > 0 else 0,
    }
    
    return render(request, 'reports/dashboard.html', context)
