from celery import shared_task
from .models import Order
from esi.views import update_order_data