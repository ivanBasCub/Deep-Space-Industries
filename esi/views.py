from django.conf import settings
from buyback.models import Manager
from .utils import esi_call, update_pages, handler
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

    url_char = f'{settings.EVE_ESI_URL}/characters/{character.character_id}/'
    response = requests.get(url=url_char, headers=headers)
    response = esi_call(response)
    data_char = response.json()
    
    if 'corporation_id' in data_char:
        url_corp = f'{settings.EVE_ESI_URL}/corporations/{data_char["corporation_id"]}/'
        response = requests.get(url=url_corp, headers=headers)
        response = esi_call(response)
        data_corp = response.json()
        character.corp_id = data_char['corporation_id']
        character.corp_name = data_corp['name']
    else:
        character.corp_id = 0
        character.corp_name = ''
        
    if 'alliance_id' in data_char:
        url_alliance =  f'{settings.EVE_ESI_URL}/alliances/{data_char["alliance_id"]}/'
        response = requests.get(url=url_alliance, headers=headers)
        response = esi_call(response)
        data_alliance = response.json()
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
    
    url = f'{settings.EVE_ESI_URL}/characters/{character.character_id}/wallet/'
    
    response = requests.get(url=url, headers=headers)
    response = esi_call(response)
    data_wallet = response.json()
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
    url = f"{settings.EVE_ESI_URL}/universe/types/{item_id}"
    response = requests.get(url=url, headers = headers)
    response = esi_call(response)
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
    
    headers_station = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-12-16",
        "X-Tenant": "",
        "If-Modified-Since": "",
        "Accept": "application/json"
    }
    url = ""
    
    if structure_id >= 100000000:
        url = f"{settings.EVE_ESI_URL}/universe/structures/{structure_id}"
        response = requests.get(url, headers=headers)
        response = esi_call(response)
    else:
        url = f"{settings.EVE_ESI_URL}/universe/stations/{structure_id}"
        response = requests.get(url, headers=headers_station)
        response = esi_call(response)

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
    response = esi_call(response)
    if response.status_code != 200:
        return {}
    
    return response.json()

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
    
    try:
        assets = update_pages(
            handler=handler,
            url=url,
            headers=headers
        )
        
        return assets
    except requests.HTTPError as e:
        return f"Error HTTP: {e.response.status_code}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


# Function to obtain the project contract status
def corp_contracts():
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
    
    try:
        contracts = update_pages(
            handler=handler,
            url=url,
            headers=headers
        )
        return contracts
    except requests.HTTPError as e:
        return f"Error HTTP: {e.response.status_code}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"