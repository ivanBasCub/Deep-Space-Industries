from celery import shared_task
from esi.views import corp_assets, item_data_id
from .models import CorpItem
from buyback.models import Manager
import json

@shared_task
def update_corp_asset():
    manager = Manager.objects.first()
    loc_flag_filter = ["CorpSAG1","CorpSAG2","CorpSAG3","CorpSAG4","CorpSAG5","CorpSAG6","Unlocked"]
    containers_id = [3296, 3293, 3297, 17366, 17367, 17368, 17365, 17364, 17363, 33003, 24445, 33005]

    data = corp_assets(manager)

    try:
        locations_info = {}
        seen_locations = set()
        
        for item in data:
            if item["type_id"] in containers_id and item["location_flag"] in loc_flag_filter and item["item_id"] not in seen_locations:
                locations_info[item["item_id"]] = item["location_flag"]
                seen_locations.add(item["item_id"])
        
        for item in data:
            if item["type_id"] not in containers_id and item["location_flag"] in loc_flag_filter:
                type_id = item["type_id"]
                item_data = item_data_id(type_id)
                item_name = item_data["name"]
                location_flag = locations_info.get(item["location_id"])
                if  not location_flag:
                    location_flag = item["location_flag"]
                
                asset, created = CorpItem.objects.get_or_create(
                    eve_id = type_id,
                    name = item_name,
                    loc_flag = location_flag,
                    defaults={
                        "quantity":item["quantity"]
                    }
                )
                
                if not created:
                    asset.quantity = item["quantity"]
                    asset.save()
                
    except KeyError as e:
        print(f"[ERROR] KeyError: {e}")
