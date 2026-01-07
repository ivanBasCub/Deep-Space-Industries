from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_initial_location(sender, **kwargs):
    from .models import Location, BuyBackServices
    # Create the base locations
    Location.objects.get_or_create(station_name = "Anywhere")
    # Create the list of services
    list_services = [
        {"name":"All Items", "desc":"This program accepts all types of items" },
        {"name":"Freight", "desc":"Items sold via this program have an added freight cost"},
        {"name":"Unpacked Items", "desc":"Unpacked items are accepted in this program" },
        {"name":"Jita Buy", "desc":"Prices are based on Jita Buy prices"},
        {"name":"Jita Sell", "desc":"Prices are based on Jita Sell prices"}
    ]
    for service in list_services:
        BuyBackServices.objects.get_or_create(
            name = service["name"],
            desc = service["desc"]
        )    


class BuybackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'buyback'

    def ready(self):
        post_migrate.connect(create_initial_location)

