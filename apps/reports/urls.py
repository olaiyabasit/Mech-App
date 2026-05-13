from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('jobs/pdf/', views.jobs_report_pdf, name='jobs_pdf'),
    path('jobs/csv/', views.jobs_export_csv, name='jobs_csv'),
    path('customers/csv/', views.customers_export_csv, name='customers_csv'),
    path('financial/pdf/', views.financial_report_pdf, name='financial_pdf'),
]