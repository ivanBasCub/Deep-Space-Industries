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
        return self.name

class BuyBackProgram(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, related_name="program_location")
    tax = models.BigIntegerField(default=0)
    manager = models.CharField(max_length=200)
    settings = models.ManyToManyField(BuyBackServices, related_name="program_services")
    freighter_task = models.BigIntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - {self.location} - {self.tax}%"
    
class ProgramSpecialTax(models.Model):
    item_id = models.BigIntegerField(default=0)
    item_name = models.CharField(max_length=255)
    special_tax = models.BigIntegerField(default=0)
    is_allowed = models.BooleanField(default=False)
    program = models.ManyToManyField(BuyBackProgram, related_name="special_taxes")
    
    def __str__(self):
        return f"{self.item_name} - {self.special_tax}"