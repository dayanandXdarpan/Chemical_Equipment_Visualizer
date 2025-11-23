"""
MongoDB Atlas Production Settings
Use this file for production deployment with MongoDB Atlas

Usage:
    Set environment variable: DJANGO_SETTINGS_MODULE=backend.settings_mongodb
    Or use: python manage.py runserver --settings=backend.settings_mongodb
"""

from .settings import *

# MongoDB Atlas Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'chemical_equipment_db',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb+srv://musicalindia777_db_user:Darpanfosseeweb@cluster0.myatkin.mongodb.net/?appName=Cluster0',
            'username': 'musicalindia777_db_user',
            'password': 'Darpanfosseeweb',
            'authMechanism': 'SCRAM-SHA-1',
            'retryWrites': True,
            'w': 'majority',
            'tls': True,
            'tlsAllowInvalidCertificates': False,
        },
        'LOGGING': {
            'version': 1,
            'loggers': {
                'djongo': {
                    'level': 'DEBUG',
                    'propagate': False,
                }
            }
        }
    }
}

# Security settings for production
DEBUG = False
ALLOWED_HOSTS = ['*']  # Update with your actual domain in production

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add your production frontend URL here
]

CORS_ALLOW_CREDENTIALS = True

# Static files for production
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Security settings
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# Session settings
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
