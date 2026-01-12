from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from sso.models import CharacterEve
from buyback.models import Manager
import esi.views as esi_views

from base64 import b64encode
from datetime import timedelta
import secrets
import random
import string
import urllib.parse
import requests

# Function to initiate EVE Online SSO login
def eve_login(request, scope, login_type):
    state = f"{login_type}_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    print(settings.CLIENT_ID)
    params = {
        'response_type': 'code',
        'client_id': settings.CLIENT_ID,
        'redirect_uri': settings.CALLBACK_URL,
        'scope': scope,
        'state': state
    }
    
    url = 'https://login.eveonline.com/v2/oauth/authorize?' + urllib.parse.urlencode(params)
    return redirect(url)

def eve_login_user(request):
    scope = "publicData"
    return eve_login(request, scope, "user")

def eve_login_manager(request):
    scope = settings.EVE_SSO_SCOPE
    return eve_login(request, scope, "manager")

# Callback function to handle EVE Online SSO response
def eve_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    login_type = state.split("_")[0]
    
    headers = {
        'Authorization' : f'Basic {b64encode(f"{settings.CLIENT_ID}:{settings.CLIENT_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.CALLBACK_URL,
    }
    
    response = requests.post('https://login.eveonline.com/v2/oauth/token', headers=headers, data=data)
    token = response.json()
    url = 'https://login.eveonline.com/oauth/verify'
    header = {
        'Authorization': f'Bearer {token["access_token"]}'
    }

    res = requests.get(url, headers=header)
    if res.status_code != 200:
        messages.error(request, "Failed to verify EVE Online user.")
        return redirect('index')
    user_info = res.json()
    
    if login_type == "user":
        return check_account(request, token, user_info)
    elif login_type == "manager":
        return save_manager(request, token, user_info)

# Function to check if the account exists and register or update accordingly
def check_account(request, token, user_info):
    if request.user.is_authenticated:
        return register_eve_account(request, token, user_info)
    else:
        return update_create_account(request, token, user_info)

# Function to register a new EVE Online account in an existing user session
# TODO: Implementar las funciones de registro de nuevas cuentas EVE Online
def register_eve_account(request, token, user_info):
    check = CharacterEve.objects.filter(character_id=user_info['CharacterID'])
    if check.exists():
        refresh_eve_character(request.user, user_info, token)
    else:
        save_eve_character(request.user, user_info, token)
    
    return redirect('dashboard')

# Function to refresh an existing EVE Online character's tokens and information
def refresh_eve_character(user, character, token):
    expiration = timezone.now() + timedelta(minutes=20)

    # character es un dict del SSO
    char = CharacterEve.objects.get(character_id=character['CharacterID'])

    char.access_token = token['access_token']
    char.refresh_token = token['refresh_token']
    char.expiration = expiration

    # Estas funciones sí necesitan request, así que lo pasamos desde fuera
    char = esi_views.corp_alliance_info(char)
    char = esi_views.wallet_info(char)

    if user.username == character['CharacterName'].replace(' ', '_'):
        char.main_character = True

    char.save()

# Function to save a new EVE Online character to the database
def save_eve_character(user, character, token):
    expiration = timezone.now() + timedelta(minutes=20)

    char = CharacterEve(
        character_id = character['CharacterID'],
        character_name = character['CharacterName'],
        main_character = False,
        access_token = token['access_token'],
        refresh_token = token['refresh_token'],
        expiration = expiration,
        user = user,
        deleted = False
    )

    if user.username == character['CharacterName'].replace(' ', '_'):
        char.main_character = True
        
    char = esi_views.corp_alliance_info(char)
    char = esi_views.wallet_info(char)

    char.save()
    
# Function to update an existing EVE Online account or create a new one for unauthenticated users
def update_create_account(request, token, user_info):
    vault = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(vault) for i in range(16))
    
    try:
        user = User.objects.get(username=user_info['CharacterName'].replace(' ', '_'))
        user.set_password(password)
        user.save()
        refresh_eve_character(request.user, user_info, token)
        login(request, user)
        
    except User.DoesNotExist:
        check = CharacterEve.objects.filter(character_id=user_info['CharacterID'])
        user = User.objects.create_user(username = user_info['CharacterName'].replace(' ', '_'))
        user.set_password(password)
        user.save()
        
        if check.exists():
            refresh_eve_character(request.user,user_info, token)
            return redirect('dashboard')
        
        save_eve_character(user, user_info, token)
        login(request, user)

    return redirect('dashboard')

# Function to Logout user
def eve_logout(request):
    logout(request)
    return redirect("/")

# Function to check the manager
def save_manager(request, token, user_info):
    expiration = timezone.now() + timedelta(minutes=20)
    
    if Manager.objects.exists():
        man = Manager.objects.first()
        man.character_id = user_info['CharacterID']
        man.character_name = user_info['CharacterName']
        man.access_token = token['access_token']
        man.refresh_token = token['refresh_token']
        man.expiration = expiration
        man = esi_views.corp_alliance_info(man)
        man = esi_views.wallet_info(man)

    else:
        man = Manager.objects.create(
            character_id = user_info['CharacterID'],
            character_name = user_info['CharacterName'],
            access_token = token['access_token'],
            refresh_token = token['refresh_token'],
            expiration = expiration,
        )
        
        man = esi_views.corp_alliance_info(man)
        man = esi_views.wallet_info(man)
        
    man.save()
    
    return redirect("/buybackprogram/")