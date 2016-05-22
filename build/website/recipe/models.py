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


class Unit(models.Model):
    full_name = models.CharField(max_length=20)
    abbreviation = models.CharField(max_length=20)

    def __str__(self):
        return str(self.abbreviation)


class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ManyToManyField(Category)

    def __str__(self):
        return str(self.name + ' - ' + self.category)


class ProductDetails(models.Model):
    product = models.ForeignKey(Product)
    barcode = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=200)
    quantity = models.IntegerField()

    def __str__(self):
        return str(self.quantity) + ' ' + self.product + ' ' + self.manufacturer


class Ingredient(models.Model):
    name = models.ForeignKey(Product)
    quantity = models.IntegerField()
    unit = models.ForeignKey(Unit)
    product = models.ForeignKey(Product)

    def __str__(self):
        return str(self.quantity) + self.unit + " " + self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient)
    description = models.CharField(max_length=1000)
    yields = models.IntegerField()
    calories = models.IntegerField()
    dietLabels = models.CharField(max_length=1000)
    healthLabels = models.CharField(max_length=1000)
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
    yields = models.IntegerField()
    time = models.TimeField()
    event = models.CharField(max_length=1024)

    def __str__(self):
        return self.name + ' ' + self.date


class ShoppingList(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Ingredient)
    card = models.CharField(max_length=1024)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name


class ProductList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(ProductDetails)
    card = models.CharField(max_length=1024)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.items
