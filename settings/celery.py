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
    'update_item_price':{
        'task':'project.tasks.update_item_price',
        'schedule': 3600,
        'args':()
    },
    'update_orders_status':{
        'task':'shop.taks.update_orders_status',
        'schedule': 300,
        'args':()
    },
    "update_corp_asset":{
        'task':'warehouse.tasks.update_corp_asset',
        'schedule': 3600,
        'args':()
    }
}

app.conf.timezone = 'Europe/Madrid'