from django.contrib import admin
from recipe.models import *

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Meal)
admin.site.register(ShoppingList)
admin.site.register(ProductList)
