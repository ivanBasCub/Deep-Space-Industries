from celery import shared_task
from .models import Order
from esi.views import update_order_data

@shared_task
def check_order_status():
    list_orders = Order.objects.filter(status__in=[0,1]).all()
    for order in list_orders:
        update_order_data(order)