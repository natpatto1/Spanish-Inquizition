from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    points = models.PositiveIntegerField(null=False, blank=False, default=0)



