from django.contrib import admin
from recipe.models import *


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'global_access')
admin.site.register(Recipe, RecipeAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'unit')
admin.site.register(Ingredient, IngredientAdmin)


class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'date')
admin.site.register(Meal, MealAdmin)


admin.site.register(ShoppingList)
admin.site.register(ProductList)
