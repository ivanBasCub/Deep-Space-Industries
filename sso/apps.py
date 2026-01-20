from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_inital_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    list_groups = ["Admin","Industry"]
    
    for group in list_groups:
        Group.objects.get_or_create(name=group)

class SsoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sso'

    def ready(self):
        post_migrate.connect(create_inital_groups, sender=self)