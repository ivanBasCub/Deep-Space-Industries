from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    contract_id = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.PositiveBigIntegerField(default=0)

class Item(models.Model):
    eve_id = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=200)
    jita_price = models.DecimalField(max_digits=20, decimal_places=2)
    volume = models.DecimalField(max_digits=20, decimal_places=6)
    
class MaterialProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="materials")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="materials")
    obtained = models.PositiveBigIntegerField(default=0)
    quantity = models.PositiveBigIntegerField()
    
    def total_price_needed(self):
        return self.item.jita_price * (self.quantity - self.obtained)
    
    def total_price(self):
        return self.item.jita_price * self.quantity

class Product(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="product")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="product")
    quantity = models.PositiveBigIntegerField()
    
    def total_price(self):
        return self.item.jita_price * self.quantity
    
class  Contract(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="contracts")
    contract_id = models.CharField(max_length=200, unique=True)
    contract_type = models.PositiveBigIntegerField()
    status = models.PositiveBigIntegerField(default=0)
    value = models.DecimalField(max_digits=20, decimal_places=2)