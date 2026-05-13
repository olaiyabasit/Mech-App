"""
URL configuration for winki_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize admin site
admin.site.site_header = "WInki Administration"
admin.site.site_title = "WInki Admin"
admin.site.index_title = "Welcome to WInki Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('apps.core.urls')),
    path('jobs/', include('apps.jobs.urls')),
    path('reports/', include('apps.reports.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add django-browser-reload in development
    if 'django_browser_reload' in settings.INSTALLED_APPS:
        urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
