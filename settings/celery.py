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
    },
    'check_orders':{
        'task':'shop.tasks.check_order_status',
        'schedule': 300,
        'args':()
    },
    'update_materials':{
        'task':'project.tasks.update_materials',
        'schedule': 900,
        'args':()
    },
    'update_project_contracts':{
        'task':'project.tasks.update_project_contracts',
        'schedule': 300,
        'args':()
    },
}

app.conf.timezone = 'Europe/Madrid'