from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from base64 import b64encode
import random
import string
import urllib.parse
import requests

def eve_login(request):
    state = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    print(settings.CLIENT_ID)
    params = {
        'response_type': 'code',
        'client_id': settings.CLIENT_ID,
        'redirect_uri': settings.CALLBACK_URL,
        'scope': settings.EVE_SSO_SCOPE,
        'state': state
    }
    
    url = 'https://login.eveonline.com/v2/oauth/authorize?' + urllib.parse.urlencode(params)
    return redirect(url)

def eve_callback(request):
    code = request.GET.get('code')
    
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
    tokens = response.json()
    url = 'https://login.eveonline.com/oauth/verify'
    header = {
        'Authorization': f'Bearer {tokens["access_token"]}'
    }

    res = requests.get(url, headers=header)
    if res.status_code != 200:
        messages.error(request, "Failed to verify EVE Online user.")
        return redirect('index')
    user_info = res.json()
    return user_info