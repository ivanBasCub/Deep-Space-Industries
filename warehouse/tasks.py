from celery import shared_task
from esi.views import corp_assets, item_data_id, structure_data
from .models import CorpItem
from buyback.models import Manager

@shared_task
def update_corp_asset():
    manager = Manager.objects.first()
    loc_flag_filter = ["CorpSAG1","CorpSAG2","CorpSAG3","CorpSAG4","CorpSAG5","CorpSAG6"]
    loc_filter = "station"
    data = corp_assets(manager)
    try:
        for item in data:
            
            if item["location_flag"] in loc_flag_filter and item["location_type"] == loc_filter:
                item_id = item["type_id"]
                item_name = item_data_id(item_id)["name"]
                station_name = structure_data(character=manager,structure_id=item["location_id"])["name"]
                
                asset, created = CorpItem.objects.get_or_create(
                    eve_id = item_id,
                    name = item_name,
                    loc_flag = item["location_flag"],
                    location = station_name,
                    defaults={
                        "quantity": item["quantity"]
                    }
                )
                
                if not created:
                    asset.quantity = item["quantity"]
                    asset.save()
    except KeyError:
        pass
                
