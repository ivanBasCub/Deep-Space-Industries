from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_corp_item_tags(sender, **kwargs):
    from .models import Tag
    list_tags = ["Ammo","Ship","Module","Mineral","Reaction","Blueprint","Structure","Decryptor","Deployable","Drone","Implant"]
    
    for tag in list_tags:
        Tag.objects.get_or_create(name = tag)

class WarehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouse'
    
    def ready(self):
        post_migrate.connect(create_corp_item_tags, sender=self)
