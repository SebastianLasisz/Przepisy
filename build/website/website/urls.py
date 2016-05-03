"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from website.views import *
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.authtoken import views


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = ('name', 'value', 'unit')


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    ingredients = serializers.StringRelatedField(many=True)

    class Meta:
        model = Recipe
        fields = ('name', 'description', 'ingredients', 'date')


class MealSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Meal
        fields = ('name', 'user', 'date', 'time')


class ShoppingListSerializer(serializers.HyperlinkedModelSerializer):
    items = serializers.StringRelatedField(many=True)

    class Meta:
        model = ShoppingList
        fields = ('name', 'description', 'items')


class ProductListSerializer(serializers.HyperlinkedModelSerializer):
    items = serializers.StringRelatedField(many=True)

    class Meta:
        model = ProductList
        fields = ('name', 'description', 'items')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.filter(global_access=True)
    serializer_class = RecipeSerializer


class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer


class ProductListViewSet(viewsets.ModelViewSet):
    queryset = ProductList.objects.all()
    serializer_class = ProductListSerializer


urlpatterns = [
                  url(r'^$', index),
                  url(r'^admin/', admin.site.urls),
                  url(r'^login/$', log_user, name='login'),
                  url(r'^logout/', logout_view),
                  url(r'^register/', register),
                  # Recipes
                  url(r'^add_recipe/', create_recipe),
                  url(r'^recipes/$', ShowAllRecipes.as_view()),
                  url(r'^recipe/(?P<pk>\d+)/$', show_recipe),
                  url(r'^delete_recipe/(?P<pk>\d+)/$', delete_recipe),
                  url(r'^edit_recipe/(?P<pk>\d+)/$', edit_recipe),
                  # Meals
                  url(r'^add_meal/', create_meal),
                  url(r'^meals/', ShowAllMeals.as_view()),
                  url(r'^meal/(?P<pk>\d+)/$', show_meal),
                  url(r'^delete_meal/(?P<pk>\d+)/$', delete_meal),
                  url(r'^edit_meal/(?P<pk>\d+)/$', edit_meal),
                  # Shopping list
                  url(r'^add_shopping_list/', create_shopping_list),
                  url(r'^shopping_lists/', ShowShoppingLists.as_view()),
                  url(r'^shopping_list/(?P<pk>\d+)/$', show_shopping_list),
                  url(r'^delete_shopping_list/(?P<pk>\d+)/$', delete_shopping_list),
                  url(r'^edit_shopping_list/(?P<pk>\d+)/$', edit_shopping_list),
                  # Product list
                  url(r'^add_product_list/', create_product_list),
                  url(r'^product_lists/', ShowProductLists.as_view()),
                  url(r'^product_list/(?P<pk>\d+)/$', show_product_list),
                  url(r'^delete_product_list/(?P<pk>\d+)/$', delete_product_list),
                  url(r'^edit_product_list/(?P<pk>\d+)/$', edit_product_list),
                  # API
                  url(r'^api-token-auth/', views.obtain_auth_token),
                  url(r'^api/own_recipe_list/', own_recipe_list),
                  url(r'^api/recipe_list/', recipe_list),
                  url(r'api/recipe/(?P<pk>\d+)/$', recipe),
                  url(r'^docs/', include('rest_framework_swagger.urls')),
                  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
