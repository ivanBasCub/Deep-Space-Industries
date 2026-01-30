from celery import shared_task
from .models import MaterialProject, Item
from buyback.models import Manager
from esi.views import corp_assets, contract_project_status, apprisal_data

@shared_task
def update_materials():
    materials = MaterialProject.objects.filter(project__status=0)
    manager = Manager.objects.first()
    assets = corp_assets(manager)
    
    asset_map = {}
    
    for asset in assets:
        item_id = asset["type_id"]
        asset_map[item_id] = asset_map.get(item_id, 0) + asset["quantity"]
        
    for material in materials: 
        material.obtained = asset_map.get(material.item.eve_id, 0)
    
    MaterialProject.objects.bulk_update(materials, ["obtained"])
    
    
@shared_task
def update_project_contracts():
    contract_project_status()
    
@shared_task
def update_item_price():
    list_items = Item.objects.all()
    
    items = ""
    for item in list_items:
        items += item.name +"\n"
        
    app_data = apprisal_data(items=items)
    
    for data in app_data["items"]:
        item = Item.objects.get(name = data["itemType"]["name"])
        item.jita_price = data["effectivePrices"]["buyPrice"] / 100
        item.volume = data["totalVolume"]
        item.save()