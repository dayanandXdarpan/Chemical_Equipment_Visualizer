"""
WSGI config for Render deployment.
This file allows Render to run the Django application using gunicorn app:app
"""
import os
import sys

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Import Django and setup
import django
django.setup()

# Import the WSGI application
from backend.wsgi import application

# Make it available as 'app' for gunicorn
app = application