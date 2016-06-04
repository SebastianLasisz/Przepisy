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
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category)

    def __str__(self):
        return str(self.name)


class ProductDetails(models.Model):
    product = models.ForeignKey(Product)
    barcode = models.CharField(max_length=200, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return str(self.quantity) + ' ' + self.product.name + ' ' + self.manufacturer


class Ingredient(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    unit = models.ForeignKey(Unit)
    calories = models.IntegerField(blank=True)
    dietLabels = models.CharField(max_length=1000, blank=True)
    healthLabels = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return str(self.quantity) + " " + self.unit.abbreviation + " " + self.product.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient)
    description = models.CharField(max_length=100, blank=True)
    recipe_steps = models.CharField(max_length=1000)
    yields = models.IntegerField()
    date = models.DateField(default=datetime.date.today)
    global_access = models.BooleanField(default=True)
    card = models.CharField(max_length=1024, blank=True)
    calories = models.IntegerField(blank=True, default=0)
    dietLabels = models.CharField(max_length=1000, blank=True)
    healthLabels = models.CharField(max_length=1000, blank=True)

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
    event = models.CharField(max_length=1024, blank=True)

    def __str__(self):
        return self.name.name


class ShoppingList(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Ingredient)
    card = models.CharField(max_length=1024, blank=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name


class ProductList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    items = models.ForeignKey(ProductDetails)
    card = models.CharField(max_length=1024, blank=True)

    class Meta:
        ordering = ["-id"]
