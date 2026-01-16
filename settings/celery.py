import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
app = Celery('settings')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'refresh_tokens':{
        'task':'sso.tasks.tokens',
        'schedule': 600,
        'args':()
    }
}

app.conf.timezone = 'Europe/Madrid'