from django.contrib import admin
from recipe.models import *


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'global_access')
admin.site.register(Recipe, RecipeAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'unit')
admin.site.register(Ingredient, IngredientAdmin)


class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'date')
admin.site.register(Meal, MealAdmin)


admin.site.register(ShoppingList)
admin.site.register(ProductList)
admin.site.register(Unit)
admin.site.register(ProductDetails)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(RecipeComment)
