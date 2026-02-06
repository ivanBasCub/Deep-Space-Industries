from celery import shared_task
from esi.views import corp_assets, item_data_id, structure_data
from .models import CorpItem
from buyback.models import Manager

@shared_task
def update_corp_asset():
    manager = Manager.objects.first()

    loc_flag_filter = ["CorpSAG1","CorpSAG2","CorpSAG3","CorpSAG4","CorpSAG5","CorpSAG6","Unlocked"]
    containers_id = [3296, 3293, 3297, 17366, 17367, 17368, 17365, 17364, 17363, 33003, 24445, 33005,27]

    data = corp_assets(manager)

    try:
        items_by_id = {i["item_id"]: i for i in data}

        def resolve_location(item, visited=None):
            """
            Sube por la cadena de items hasta encontrar un location_flag en loc_flag_filter.
            Evita loops usando un set de items visitados.
            """
            if visited is None:
                visited = set()

            current = item
            while current:
                if current["item_id"] in visited:
                    return None
                visited.add(current["item_id"])

                if current["location_flag"] in loc_flag_filter:
                    return current["location_flag"]

                if current.get("location_type") == "item":
                    parent = items_by_id.get(current["location_id"])
                    if not parent:
                        return None
                    current = parent
                else:
                    return None
            return None

        for item in data:
            if item["type_id"] in containers_id:
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
