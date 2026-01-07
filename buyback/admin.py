from django.contrib import admin
import buyback.models as models
# Register your models here.
admin.site.register(models.BuyBackProgram)
admin.site.register(models.Location)
admin.site.register(models.BuyBackServices)
admin.site.register(models.ProgramSpecialTax)