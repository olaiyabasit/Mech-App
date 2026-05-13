from .base import *
import os
import dj_database_url

# Security Settings for Production
DEBUG = False
ALLOWED_HOSTS = ['.vercel.app', '.vercel.com', '.railway.app', '.up.railway.app']

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = False  # Railway handles SSL at the proxy level
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = ['https://*.railway.app', 'https://*.up.railway.app']
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Database Configuration
DATABASES = {
    'default': dj_database_url.config(env='DATABASE_URL', conn_max_age=600)
}

# Static Files for Production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Django 5.2 uses STORAGES dict — the old STATICFILES_STORAGE key is ignored.
# Use WhiteNoise compressed manifest storage for hashed filenames + gzip.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # CompressedStaticFilesStorage: gzip/brotli compression without URL
        # rewriting. CompressedManifestStaticFilesStorage rewrites @import
        # references inside CSS which breaks Tailwind v4's @import directives.
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}