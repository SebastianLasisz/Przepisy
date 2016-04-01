from django.db import models
import datetime


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    value = models.IntegerField()
    unit = models.CharField(max_length=20)


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(Ingredient)
    description = models.CharField(max_length=1000)
    global_access = models.BooleanField()


class Meal(models.Model):
    name = models.OneToOneField(Recipe)
    date = models.DateField(default=datetime.date.today)
    time = models.TimeField()


class ShoppingList(models.Model):
    name = models.CharField(max_length=200)
    items = models.ManyToManyField(Ingredient)


class ProductList(models.Model):
    name = models.CharField(max_length=200)
    items = models.ManyToManyField(Ingredient)
