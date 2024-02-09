from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

    
class Party(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    delete_flag = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        unique_together = ['user','name', 'phone_number']
    
class Form(models.Model):
    created_at = models.DateField(unique=True)

class Transaction(models.Model):
    party = models.ForeignKey(Party,on_delete=models.CASCADE)
    description = models.TextField(blank=True,null=True)
    debit = models.PositiveIntegerField(default=0)
    credit = models.PositiveIntegerField(default=0)
    form = models.ForeignKey(Form,on_delete = models.CASCADE)