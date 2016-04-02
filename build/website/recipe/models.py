from django.db import models
from django.contrib.auth.models import User
import datetime


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    value = models.IntegerField()
    unit = models.CharField(max_length=20)


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient)
    description = models.CharField(max_length=1000)
    date = models.DateField(default=datetime.date.today)
    global_access = models.BooleanField()

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name


class Meal(models.Model):
    name = models.OneToOneField(Recipe)
    user = models.OneToOneField(User)
    date = models.DateField(default=datetime.date.today)
    time = models.TimeField()


class ShoppingList(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    items = models.ManyToManyField(Ingredient)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name + self.description


class ProductList(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    items = models.ManyToManyField(Ingredient)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name + self.description
