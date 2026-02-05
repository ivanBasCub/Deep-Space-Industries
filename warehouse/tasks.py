from celery import shared_task
from esi.views import corp_assets, item_data_id, structure_data
from .models import CorpItem
from buyback.models import Manager

@shared_task
def update_corp_asset():
    manager = Manager.objects.first()
    loc_flag_filter = ["CorpSAG1","CorpSAG2","CorpSAG3","CorpSAG4","CorpSAG5","CorpSAG6"]
    containers_id = [16041,11490,33003,24445,16043,11489,56362,33005,11488,17365,33007,16045,3465,3296,27803,17364,33009,3466,16042,3293,2263,17363,33011,16044,3467,3297,28868,17366,17367,17368]
    loc_filter = ["station","item"]
    data = corp_assets(manager)

    try:
        station_items = []
        seen_ids = set()
        
        for item in data:
            if (
                item["location_type"] == "station" and item["type_id"] in containers_id and item["item_id"] not in seen_ids
            ):
                print("[INFO] Contenedor encontrado")
                station_items.append({
                    "item_id": item["item_id"], 
                    "location_flag": item["location_flag"], 
                    "location_id": item["location_id"]
                })
                seen_ids.add(item["item_id"])
        
        print("[INFO] Lista de contenedores")
        print(station_items)
        
        for item in data:
            if item["location_type"] in loc_filter and item["type_id"] not in containers_id:
                item_id = item["type_id"]
                item_name = item_data_id(item_id)["name"]

                structure_id = item["location_id"]
                loc_flag = item["location_flag"]

                if item["location_id"] in seen_ids:
                    container = next(
                        (c for c in station_items if c["item_id"] == item["location_id"]),
                        None
                    )

                    if container:
                        loc_flag = container["location_flag"]
                        structure_id = container["location_id"]

                station_name = structure_data(character=manager, structure_id=structure_id)["name"]
                
                asset, created = CorpItem.objects.get_or_create(
                    eve_id=item_id,
                    name=item_name,
                    loc_flag=loc_flag,
                    location=station_name,
                    defaults={"quantity": item["quantity"]}
                )
                
                if not created:
                    asset.quantity = item["quantity"]
                    asset.save()

    except KeyError:
        pass
