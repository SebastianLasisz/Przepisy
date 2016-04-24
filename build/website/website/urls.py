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


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.


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
                  url(r'^test_api/', include(router.urls)),
                  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
