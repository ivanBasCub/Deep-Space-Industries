from celery import shared_task
from .models import MaterialProject, Item
from buyback.models import Manager
from .models import Project, Contract
from esi.views import corp_assets, corp_contracts, apprisal_data

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
    contrats = corp_contracts()
    print(contrats)
    if not isinstance(contrats, list):
        return "[ERROR] Formato incorrecto"
    
    for contract in contrats:
        data = contract["title"].split("-")
        if len(data) != 4:
            continue
        
        try:
            project_id = int(data[1])
            contract_type = int(data[2])
        except ValueError:
            continue
        
        status = 0
        project = Project.objects.filter(id=project_id).first()
        if not project:
            continue
        match contract["status"]:
            case "outstanding":
                status = 1
            case "finished":
                status = 2
            case "cancelled":
                status = 3
            case "deleted":
                status = 4
            case _:
                status = 0

        project = Project.objects.get(id=project_id)
        contractBBDD, created = Contract.objects.get_or_create(
            project = project,
            contract_id = contract["title"],
            defaults={
                "contract_type": contract_type,
                "status": status,
                "value": contract["price"]
            }
        )
        
        if not created:
            contractBBDD.status = status
            contractBBDD.value = contract["price"]
            contractBBDD.save()
    
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