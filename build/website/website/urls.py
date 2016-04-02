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
    url(r'^shopping_list/', edit_shopping_list),
    # Product list
    url(r'^product_list/', edit_product_list),
]
