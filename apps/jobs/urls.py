from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('qr/<str:qr_code>/', views.qr_code_lookup, name='qr_lookup'),
    path('qr-image/<str:job_id>/', views.generate_qr_code_image, name='qr_image'),
    path('api/status/<str:qr_code>/', views.job_status_api, name='status_api'),
]