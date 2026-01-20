from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    item_id = models.PositiveBigIntegerField(default=0)
    item_name = models.CharField(max_length=255)
    quantity = models.PositiveBigIntegerField(default=0)
    price = models.FloatField(default=0)
    status = models.BooleanField(default=False)

class Order(models.Model):
    order_id = models.CharField(max_length=30, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.PositiveBigIntegerField(default=0)
    
    def __str__(self):
        return f"Order for user {self.user.username}"
    
    def total_items(self):
        return sum(item.quantity for item in self.order_items.all())
    
    def total_price(self):
        return sum(item.subtotal() for item in self.order_items.all())
    
class ItemsOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="items")
    quantity = models.PositiveBigIntegerField(default=1)
    
    class Meta:
        unique_together = ('order','item')
    
    def __str__(self):
        return f"{self.item.item_name} x{self.quantity}"
    
    def subtotal(self):
        return self.item.price * self.quantity    