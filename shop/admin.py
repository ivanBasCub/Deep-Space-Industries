from django.contrib import admin
from .models import Item, ItemsOrder, Order

admin.site.register(Item)
admin.site.register(ItemsOrder)
admin.site.register(Order)
