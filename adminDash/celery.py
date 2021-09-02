import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adminDash.settings')

app = Celery('adminDash')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()