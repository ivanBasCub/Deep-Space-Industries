from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=255,default="")
    
class CorpItem(models.Model):
    eve_id = models.PositiveBigIntegerField(default=0)
    name = models.CharField(max_length=255, default="")
    quantity = models.PositiveBigIntegerField(default=0)
    loc_flag = models.CharField(max_length=255, default="")
    
class CorpItem_Tag(models.Model):
    item = models.ForeignKey(CorpItem, models.CASCADE, related_name="items")
    tag = models.ForeignKey(Tag, models.CASCADE, related_name="tags")
