from django.db import models

class BuyBackServices(models.Model):
    name = models.CharField(max_length=255)
    desc = models.TextField(default="")
    
    def __str__(self):
        return self.name

class Location(models.Model):
    station_id = models.BigIntegerField(default=0)
    station_name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.station_name
    
class Manager(models.Model):
    unique_id = models.AutoField(primary_key=True)
    character_id = models.BigIntegerField(default=0)
    character_name = models.CharField(max_length=255)
    
    access_token = models.TextField(default='')
    refresh_token = models.CharField(max_length=100)
    expiration = models.DateTimeField(null=True, blank=True)
    
    corp_id = models.BigIntegerField(default=0)
    corp_name = models.CharField(max_length=255, default='')
    alliance_id = models.BigIntegerField(default=0)
    alliance_name = models.CharField(max_length=255, default='')
    
    wallet_money = models.BigIntegerField(default=0)
    deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.character_name} ({self.character_id})"
    
class BuyBackProgram(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, related_name="program_location")
    tax = models.BigIntegerField(default=0)
    manager = models.ForeignKey(Manager, on_delete=models.DO_NOTHING, related_name="program_manager")
    settings = models.ManyToManyField(BuyBackServices, related_name="program_services")
    freighter_tax = models.BigIntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - {self.location} - {self.tax}%"
    
class ProgramSpecialTax(models.Model):
    item_id = models.BigIntegerField(default=0)
    item_name = models.CharField(max_length=255)
    special_tax = models.BigIntegerField(default=0)
    is_allowed = models.BooleanField(default=False)
    program = models.ForeignKey(BuyBackProgram, on_delete=models.DO_NOTHING, related_name="program_special_taxes", null=True)
    
    def __str__(self):
        return f"{self.item_name} - {self.special_tax}"