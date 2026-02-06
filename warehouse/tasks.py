from celery import shared_task
from esi.views import corp_assets, item_data_id, structure_data
from .models import CorpItem
from buyback.models import Manager
import json

@shared_task
def update_corp_asset():
    manager = Manager.objects.first()
    loc_flag_filter = ["CorpSAG1","CorpSAG2","CorpSAG3","CorpSAG4","CorpSAG5","CorpSAG6","Unlocked"]
    containers_id = [3296, 3293, 3297, 17366, 17367, 17368, 17365, 17364, 17363, 33003, 24445, 33005]

    data = corp_assets(manager)

    if isinstance(data, str):
        data = json.loads(data)

    data = [i for i in data if isinstance(i, dict)]

    try:
        items_by_id = {i["item_id"]: i for i in data if "item_id" in i}

        def resolve_location(item, visited=None):
            if visited is None:
                visited = set()

            current = item
            while current:
                if not isinstance(current, dict) or "item_id" not in current:
                    return None

                if current["item_id"] in visited:
                    return None
                visited.add(current["item_id"])

                if current.get("location_flag") in loc_flag_filter:
                    return current["location_flag"]

                if current.get("location_type") == "item":
                    parent = items_by_id.get(current.get("location_id"))
                    if not parent:
                        return None
                    current = parent
                else:
                    return None
            return None

        for item in data:
            if not isinstance(item, dict) or "type_id" not in item:
                continue

            # Filtrado: no guardar contenedores ni type_id 27
            if item["type_id"] in containers_id or item["type_id"] == 27:
                continue

            loc_flag = resolve_location(item)
            if not loc_flag:
                continue

            item_id = item["type_id"]
            item_name = item_data_id(item_id)["name"]
            if item.get("is_blueprint_copy", False):
                item_name += " (Copy)"

            asset, created = CorpItem.objects.get_or_create(
                eve_id=item_id,
                name=item_name,
                loc_flag=loc_flag,
                location=loc_flag,
                defaults={"quantity": item["quantity"]}
            )

            if not created:
                asset.quantity = item["quantity"]
                asset.save()

    except KeyError as e:
        print(f"[ERROR] KeyError: {e}")
