from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

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