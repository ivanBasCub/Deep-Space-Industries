from django.contrib import admin
from .models import Project, MaterialProject, Contract, Item, Product

# Register your models here.
admin.site.register(Project)
admin.site.register(MaterialProject)
admin.site.register(Contract)
admin.site.register(Item)
admin.site.register(Product)