from celery import shared_task
from esi.views import corp_contracts
from .models import Order

@shared_task
def update_orders_status():
    contract_orders = corp_contracts()
    
    if isinstance(contract_orders, (dict, list)):
        return "[ERROR] Formato incorrecto"
    
    list_orders = Order.objects.filter(status__in=[0,1])
    
    for contract in contract_orders:
        order_id = contract["title"]
        
        try:
            order = list_orders.get(order_id=order_id)
        except Order.DoesNotExist:
            continue
        except Order.MultipleObjectsReturned: 
            continue
        
        status_map = {
            "outstanding": 1, 
            "finished": 2, 
            "cancelled": 3, 
            "deleted": 4,
        }
        new_status = status_map.get(contract["status"], 0)
        
        if order.status != new_status:
            order.status = new_status
            order.save()
            