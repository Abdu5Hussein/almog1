import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Almog1.settings')

app = Celery('almog1')

# Load Django settings and configure Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks in Django apps
app.autodiscover_tasks()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

app = Celery('your_project_name')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
