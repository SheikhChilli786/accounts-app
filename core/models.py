from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    phone_number = models.CharField(unique=True)
    question = models.TextField(blank=True,null=True)
    answer = models.TextField(blank=True,null=True)
    