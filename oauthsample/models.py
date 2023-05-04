from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


# Create your models here.
class Product(models.Model):
    name = models.CharField('name', max_length=512)
    price = models.FloatField('price', default=0.0)
    quantity = models.IntegerField('quantity', default=0)
    image = models.ImageField(upload_to='images', max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EmailToken(models.Model):
    """
        This model is to store tokens for email verification
    """
    token = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_expired = models.BooleanField(default=False)
    expires_at = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
