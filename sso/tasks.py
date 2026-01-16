from celery import shared_task
from .views import refresh_access_token
from .models import CharacterEve
from buyback.models import Manager

@shared_task
def tokens():
    list_characters = CharacterEve.objects.all()
    manager = Manager.objects.first()
    
    refresh_access_token(manager)
    for char in list_characters:
        refresh_access_token(char)