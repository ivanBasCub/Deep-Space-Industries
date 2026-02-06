from celery import shared_task
from esi.views import corp_assets, item_data_id, structure_data
from .models import CorpItem
from buyback.models import Manager

@shared_task
def update_corp_asset():
    manager = Manager.objects.first()

    loc_flag_filter = ["CorpSAG1","CorpSAG2","CorpSAG3","CorpSAG4","CorpSAG5","CorpSAG6", "Unlocked"]
    containers_id = [3296, 3293, 3297, 17366, 17367, 17368, 17365, 17364, 17363, 33003, 24445, 33005]
    loc_filter = {"station", "item"}

    data = corp_assets(manager)

    try:
        station_items = []
        seen_ids = set()
        
        for item in data:
            if (
                item["location_type"] == "item"
                and item["type_id"] in containers_id
                and item["item_id"] not in seen_ids
                and item["location_flag"] in loc_flag_filter
            ):

                station_items.append({
                    "item_id": item["item_id"],
                    "location_flag": item["location_flag"],
                    "location_id": item["location_id"],  # station_id
                })
                seen_ids.add(item["item_id"])

        items_by_id = {i["item_id"]: i for i in data}

        def resolve_station(item):
            loc_flag = item["location_flag"]
            current = item

            while current and current.get("location_type") == "item":
                parent_id = current["location_id"]

                container = next(
                    (c for c in station_items if c["item_id"] == parent_id),
                    None
                )
                if container:
                    return container["location_id"], container["location_flag"]

                current = items_by_id.get(parent_id)

            if current and current.get("location_type") == "station":
                return current["location_id"], loc_flag

            return None, None

        
        for item in data:
            if item["location_type"] in loc_filter and item["type_id"] not in containers_id and item["location_flag"] in loc_flag_filter:

                structure_id, loc_flag = resolve_station(item)
                if not structure_id:
                    continue

                item_id = item["type_id"]
                item_name = item_data_id(item_id)["name"]

                station_name = structure_data(
                    character=manager,
                    structure_id=structure_id
                )["name"]

                if "is_blueprint_copy" in item:
                    if item["is_blueprint_copy"]:
                        item_name = item_name + " (Copy)"
                
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

    except KeyError as e:
        print(f"[ERROR] KeyError: {e}")

