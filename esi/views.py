from django.conf import settings
from buyback.models import Manager
from project.models import Project, Contract
import requests

# Function to get corporation and alliance info for a character
def corp_alliance_info(character):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json"
    }

    response_char = requests.get(f'{settings.EVE_ESI_URL}/characters/{character.character_id}/', headers=headers)
    if response_char.status_code != 200:
        return character
    data_char = response_char.json()
    
    if 'corporation_id' in data_char:
        response_corp = requests.get(f'{settings.EVE_ESI_URL}/corporations/{data_char["corporation_id"]}/', headers=headers)
        data_corp = response_corp.json()
        character.corp_id = data_char['corporation_id']
        character.corp_name = data_corp['name']
    else:
        character.corp_id = 0
        character.corp_name = ''
        
    if 'alliance_id' in data_char:
        response_alliance = requests.get(f'{settings.EVE_ESI_URL}/alliances/{data_char["alliance_id"]}/', headers=headers)
        data_alliance = response_alliance.json()
        character.alliance_id = data_char['alliance_id']
        character.alliance_name = data_alliance['name']
    else:
        character.alliance_id = 0
        character.alliance_name = ''

    return character

# Function to get wallet information for a character
def wallet_info(character):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.access_token}"
    }
    
    response_wallet = requests.get(f'{settings.EVE_ESI_URL}/characters/{character.character_id}/wallet/', headers=headers)
    if response_wallet.status_code != 200:
        return character
    data_wallet = response_wallet.json()
    character.wallet_money = data_wallet
    
    return character

# Function obtain EvE Item Data
def item_data_id(item_id):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json"
    }

    response = requests.get(f"{settings.EVE_ESI_URL}/universe/types/{item_id}", headers = headers)
    return response.json()
    
# Function obtain structures data
def structure_data(character, structure_id):
  
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-12-16",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.access_token}"
    }
    print(character.access_token)
    
    response = requests.get(
        f"{settings.EVE_ESI_URL}/universe/structures/{structure_id}",
        headers=headers
    )
    print(response.status_code)
    return response.json()

# Function to obtain the apprasial
def apprisal_data(items, program = False):
    headers = {
        "accept":"application/json",
        "Content-Type":"text/plain",
        "X-ApiKey" : settings.JANICE_API_KEY
    }
    
    jita_price = "buy" if getattr(program, "jita_buy", False) else "sell"
    
    url = f"{settings.JANICE_API_URL}appraisal?market=2&designation=appraisal&pricing={jita_price}&pricingVariant=immediate&persist=false&compactize=true&pricePercentage=100"
    response = requests.post(url, headers=headers, data=items)
    if response.status_code != 200:
        return {}
    
    return response.json()

# Function to obtain the contract data from the ESI API
def update_order_data(order):
    manager = Manager.objects.first()
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-12-16",
        "X-Tenant": "",
        "If-Modified-Since": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {manager.access_token}"
    }
    
    url = f"{settings.EVE_ESI_URL}/corporations/{manager.corp_name}/contracts/"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return 1
    
    contracts = response.json()

    for contract in contracts:
        if contract['title'] == order.order_id:
            match contract["status"]:
                case "outstanding":
                    order.status = 1
                case "completed":
                    order.status = 2
                case "cancelled":
                    order.status = 3
                case "deleted":
                    order.status = 4
                case _:
                    order.status = 0 

    order.save()
    if order.status == 3 or order.status == 4:
        list_items = order.order_items.all()
        for item_order in list_items:
            item = item_order.item
            item.quantity += item_order.quantity
            item.save()

    return 0

# Function to obtain the corporation assets
def corp_assets(manager):
    
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-12-16",
        "X-Tenant": "",
        "If-Modified-Since": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {manager.access_token}"
    }
    
    url = f"{settings.EVE_ESI_URL}/corporations/{manager.corp_id}/assets/"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    
    return response.json()

# Function to obtain the project contract status
def contract_project_status():
    manager = Manager.objects.first()
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-12-16",
        "X-Tenant": "",
        "If-Modified-Since": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {manager.access_token}"
    }
    
    url = f"{settings.EVE_ESI_URL}/corporations/{manager.corp_id}/contracts/"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Error: {response.status_code}"

    contracts = response.json()
    
    for contract in contracts:
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
    
    return 0