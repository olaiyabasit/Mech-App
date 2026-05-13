from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('new/', views.job_create, name='create'),
    path('<str:pk>/', views.job_detail, name='detail'),
    path('<str:pk>/edit/', views.job_edit, name='edit'),
    path('<str:pk>/delete/', views.job_delete, name='delete'),
    path('<str:pk>/status/', views.job_update_status, name='update_status'),
    path('qr/<str:qr_code>/', views.qr_code_lookup, name='qr_lookup'),
    path('qr-image/<str:job_id>/', views.generate_qr_code_image, name='qr_image'),
    path('api/status/<str:qr_code>/', views.job_status_api, name='status_api'),
]
