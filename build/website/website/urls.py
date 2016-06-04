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
from rest_framework.authtoken import views


urlpatterns = [
                  url(r'^$', index),
                  url(r'^admin/', admin.site.urls),
                  url(r'^login/$', log_user, name='login'),
                  url(r'^logout/', logout_view),
                  url(r'^register/', register),
                  url(r'profile/', profile),
                  url(r'^summernote/', include('django_summernote.urls')),
                  # Recipes
                  url(r'^add_recipe/', create_recipe),
                  url(r'^recipes/$', ShowAllRecipes.as_view()),
                  url(r'^recipe/(?P<pk>\d+)/$', show_recipe),
                  url(r'^delete_recipe/(?P<pk>\d+)/$', delete_recipe),
                  url(r'^edit_recipe/(?P<pk>\d+)/$', edit_recipe),
                  url(r'^get_ingredients_details_for_recipe/(?P<pk>\d+)/$', get_ingredients_details_for_recipe),
                  url(r'^recipe/(?P<pk>\d+)/uprate/$', uprate_recipe),
                  url(r'^recipe/(?P<pk>\d+)/downrate/$', downrate_recipe),
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
                  url(r'^get_ingredients_details_for_shoppinglist/(?P<pk>\d+)/$', get_ingredients_details_for_shoppinglist),
                  # Product list
                  url(r'^add_product/', create_product_list),
                  url(r'^product_lists/', ShowProductLists.as_view()),
                  url(r'^product/(?P<pk>\d+)/$', show_product_list),
                  url(r'^delete_product/(?P<pk>\d+)/$', delete_product_list),
                  url(r'^edit_product/(?P<pk>\d+)/$', edit_product_list),
                  # API
                  url(r'^api-token-auth/', views.obtain_auth_token),
                  # RECIPE API
                  url(r'^api/own_recipe_list/', own_recipe_list),
                  url(r'^api/recipe_list/', recipe_list),
                  url(r'^api/add_recipe/', post_recipe),
                  url(r'^api/recipe/(?P<pk>\d+)/$', recipe),
                  # SHOPPING LIST API
                  url(r'^api/shopping_lists/', shopping_list_list),
                  url(r'^api/shopping_list/(?P<pk>\d+)/$', shopping_list),
                  url(r'^api/add_shopping_list/', post_shopping_list),
                  # PRODUCT LIST API
                  url(r'^api/product_lists/', product_list_list),
                  url(r'^api/product_list/(?P<pk>\d+)/$', product_list),
                  url(r'^api/add_product_list/', post_product_list),
                  # MEAL API
                  url(r'^api/meals/', meal_list),
                  url(r'^api/add_meal/', post_meal),
                  url(r'^api/meal/(?P<pk>\d+)/$', meal),
                  url(r'^docs/', include('rest_framework_swagger.urls')),
                  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
