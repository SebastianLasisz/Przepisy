from django.db import models
from django.contrib.auth.models import User
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    value = models.IntegerField()
    unit = models.CharField(max_length=20)

    def __str__(self):
        return str(self.value) + self.unit + " " + self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient)
    description = models.CharField(max_length=1000)
    date = models.DateField(default=datetime.date.today)
    global_access = models.BooleanField(default=True)
    card = models.CharField(max_length=1024)

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name


class Meal(models.Model):
    name = models.ForeignKey(Recipe)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    time = models.TimeField()
    event = models.CharField(max_length=1024)


class ShoppingList(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    items = models.ManyToManyField(Ingredient)
    card = models.CharField(max_length=1024)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name + self.description


class ProductList(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    items = models.ManyToManyField(Ingredient)
    card = models.CharField(max_length=1024)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name + self.description
