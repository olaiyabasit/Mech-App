from .base import *

# Development-specific settings
DEBUG = True

# Add browser-reload for development
INSTALLED_APPS += [
    'django_browser_reload',
]

MIDDLEWARE += [
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

# Tailwind settings
TAILWIND_APP_NAME = 'theme'

# Internal IPs for django-browser-reload
INTERNAL_IPS = [
    '127.0.0.1',
]