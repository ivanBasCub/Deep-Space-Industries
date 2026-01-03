from django.db import models
from django.contrib.auth.models import User

class CharacterEve(models.Model):
    character_id = models.BigIntegerField(primary_key=True)
    character_name = models.CharField(max_length=255)
    main_character = models.BooleanField(default=False)
    
    access_token = models.TextField(default='')
    refresh_token = models.CharField(max_length=100)
    expiration = models.DateTimeField(null=True, blank=True)
    
    corp_id = models.BigIntegerField(default=0)
    corp_name = models.CharField(max_length=255, default='')
    alliance_id = models.BigIntegerField(default=0)
    alliance_name = models.CharField(max_length=255, default='')
    
    wallet_money = models.BigIntegerField(default=0)
    
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='characters_eve')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.character_name} ({self.character_id})"