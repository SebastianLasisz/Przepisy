from __future__ import print_function
import httplib2
import os
from apiclient import discovery
import oauth2client
from oauth2client import file, client, tools
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import logout, authenticate, login
from django.template.context_processors import csrf
from django.forms.formsets import formset_factory
from django.shortcuts import render

from extended_user.form import *
from extended_user.models import *
from recipe.form import *
from recipe.models import *
from django.contrib.auth.hashers import make_password
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from trello import TrelloClient
import datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers
from django.conf import settings
from django.contrib import messages
import json
import urllib2


def index(request):
    return render_to_response('index.html', locals(), RequestContext(request))


def log_user(request):
    context = RequestContext(request)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')
    else:
        return render_to_response('login.html', locals(), RequestContext(request))


def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            use_google = form.cleaned_data['use_google']
            use_trello = form.cleaned_data['use_trello']
            trello_key = form.cleaned_data['trello_key']
            trello_board_name = form.cleaned_data['trello_board_name']

            userProfile = UserProfile.objects.get(user=request.user)
            userProfile.use_google = use_google
            userProfile.use_trello = use_trello
            userProfile.trello_key = trello_key
            userProfile.trello_board_name = trello_board_name
            userProfile.save()
        else:
            return render_to_response('profile.html', locals(), RequestContext(request))
        messages.add_message(request, messages.SUCCESS, 'Your profile was updated successfully')
        return HttpResponseRedirect('/profile')
    else:
        userProfile = UserProfile.objects.get(user=request.user)
        form = UserProfileForm(initial={'use_google': userProfile.use_google, 'use_trello': userProfile.use_trello,
                                        'trello_key': userProfile.trello_key,
                                        'trello_board_name': userProfile.trello_board_name})

    return render(request, 'profile.html', {
        'form': form,
        'title': 'User Profile',
        'trello': settings.TRELLO_APP_KEY
    })


@login_required
def logout_view(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'You have been logged out.')
    return HttpResponseRedirect('/')


def register(request):
    if request.method == 'POST':
        form = RegisterNewUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            repeat_password = form.cleaned_data['repeat_password']
            if password == repeat_password:
                r = User(username=username,
                         email=email,
                         password=make_password(password))
                try:
                    r.save()
                    us = UserProfile(user=r, use_google=False, use_trello=False, trello_key='', trello_board_name='')
                    us.save()
                except:
                    error = "That user name is already taken"
                    return render_to_response('register.html', locals(), RequestContext(request))
            else:
                error = "Passwords do not match"
                return render_to_response('register.html', locals(), RequestContext(request))

        else:
            return render_to_response('register.html', locals(), RequestContext(request))
        messages.add_message(request, messages.SUCCESS, 'Your account was created.')
        return HttpResponseRedirect('/')
    else:
        form = RegisterNewUserForm()
    return render(request, 'register.html', {
        'form': form
    })


@login_required
def create_meal(request):
    if request.method == 'POST':
        form = AddNewMeal(request.POST, user=request.user)
        if form.is_valid():
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                name = form.cleaned_data['name']
                recipe = Recipe.objects.filter(name=name)[0]
                date = form.cleaned_data['date']
                time = form.cleaned_data['time']
                yields = form.cleaned_data['yields']
                meal = Meal(user=request.user, name=recipe, date=date, time=time, yields=yields)
                meal.save()

                if user_profile.use_google:
                    add_event(name, meal, recipe, date, time)
            except:
                error = "That recipe doesn't exist"
                return render_to_response('create.html', locals(), RequestContext(request))
        else:
            return render_to_response('create.html', locals(), RequestContext(request))
        messages.add_message(request, messages.SUCCESS, 'Your meal was added successfully')
        return HttpResponseRedirect('/meal/' + str(meal.id))

    else:
        form = AddNewMeal(user=request.user)

    return render(request, 'create.html', {
        'form': form,
        'name': 'Create Meal'
    })


@login_required
def edit_meal(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    meal = Meal.objects.get(id=pk)
    if request.method == 'POST':
        form = EditMeal(request.POST)
        if form.is_valid():
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                meal.date = form.cleaned_data['date']
                yields = form.cleaned_data['yields']
                meal.time = form.cleaned_data['time']
                meal.save()
                if user_profile.use_google:
                    update_event(meal.event, meal.name, meal.date, meal.time)
            except:
                error = "That recipe doesn't exist"
                return render_to_response('create.html', locals(), RequestContext(request))
        else:
            return render_to_response('create.html', locals(), RequestContext(request))
        messages.add_message(request, messages.SUCCESS, 'Your meal was updated successfully')
        return HttpResponseRedirect('/meal/' + str(meal.id))
    else:
        form = EditMeal(initial={'name': meal.name, 'date': meal.date, 'time': meal.time, 'yields': meal.yields})

    return render(request, 'edit_meal.html', {
        'form': form,
        'id': pk,
        'name': 'Create Meal'
    })


class ShowAllMeals(LoginRequiredMixin, ListView):
    context_object_name = 'meal'
    queryset = Meal.objects.all()

    def get_context_data(self, **kwargs):
        queryset = Meal.objects.filter(user=self.request.user)
        context = {
            'paginator': None,
            'page_obj': None,
            'is_paginated': False,
            'object_list': queryset,
        }
        context.update(kwargs)
        return context


@login_required
def show_meal(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    try:
        meal = Meal.objects.get(id=pk)
        return render_to_response('meal.html', locals(), RequestContext(request))
    except:
        return HttpResponse(status=404)


@login_required
def delete_meal(request, **kwargs):
    user_profile = UserProfile.objects.get(user=request.user)
    pk = int(kwargs.get('pk', None))
    meal = Meal.objects.get(id=pk)
    id_to_remove = meal.event
    meal.delete()
    if user_profile.use_google:
        delete_event(id_to_remove)
    messages.add_message(request, messages.SUCCESS, 'Your meal was deleted successfully')
    return HttpResponseRedirect('/meals')


@login_required
def create_recipe(request):
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    new_recipe_formset = formset_factory(AddIngredient, max_num=10, formset=RequiredFormSet)
    if request.method == 'POST':
        recipe_form = AddNewRecipe(request.POST)
        ingredient_formset = new_recipe_formset(request.POST)

        if recipe_form.is_valid() and ingredient_formset.is_valid():
            recipe = Recipe(user=request.user, description=recipe_form.cleaned_data["description"],
                            name=recipe_form.cleaned_data["name"], yields=recipe_form.cleaned_data['yields'],
                            recipe_steps=recipe_form.cleaned_data['recipe_steps'],
                            global_access=recipe_form.cleaned_data["Available to everyone"])
            recipe.save()
            for f in ingredient_formset:
                cat = f.cleaned_data['category_name']
                try:
                    category = Category.objects.filter(name=cat)[0]
                except:
                    category = Category(name=cat)
                    category.save()
                product = Product(name=f.cleaned_data['product_name'], category=category)
                product.save()
                unit = Unit.objects.get(abbreviation=f.cleaned_data['unit'])
                quantity = f.cleaned_data['quantity']

                ingredient_api_name = str(f.cleaned_data['quantity']) + '%20' + unit.abbreviation + '%20' + product.name
                req = urllib2.Request(
                    'https://api.edamam.com/api/nutrition-data?app_id=' + settings.EDAMAM_API_ID + '&app_key=' + settings.EDAMAM_API_KEY + '&ingr=' + ingredient_api_name,
                    None, {'user-agent': 'syncstream/vimeo'})
                opener = urllib2.build_opener()
                f = opener.open(req)
                jsonData = json.JSONDecoder('latin1').decode(f.read())

                calories = jsonData['calories']
                dietLabels = jsonData['dietLabels']
                healthLabels = jsonData['healthLabels']

                ingredient = Ingredient(product=product, quantity=quantity,
                                        unit=unit, calories=calories, dietLabels=dietLabels, healthLabels=healthLabels)
                ingredient.save()
                recipe.ingredients.add(ingredient)
                recipe.save()
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.use_trello:
                add_card_trello('Recipe', recipe, recipe.name, recipe.description, recipe.ingredients,
                                user_profile.trello_key)
            messages.add_message(request, messages.SUCCESS, 'Your recipe was added successfully')
            return HttpResponseRedirect('/recipe/' + str(recipe.id))
    else:
        recipe_form = AddNewRecipe()
        ingredient_formset = new_recipe_formset()

    c = {'recipe_form': recipe_form,
         'formset_name': "Ingredients",
         'form_name': "Recipe",
         'view_name': "Create recipe",
         'ingredient_formset': ingredient_formset,
         }
    c.update(csrf(request))
    return render_to_response('create_formset.html', c, RequestContext(request))


@login_required
def delete_recipe(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    recipe = Recipe.objects.get(id=pk)
    recipe.delete()
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.use_trello:
        card_id = recipe.card
        remove_card_trello(card_id, user_profile.trello_key)
    messages.add_message(request, messages.SUCCESS, 'Your recipe was removed successfully')
    return HttpResponseRedirect('/recipes')


@login_required
def edit_recipe(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    recipe = Recipe.objects.get(id=pk)

    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    new_recipe_formset = formset_factory(AddIngredient, max_num=10, formset=RequiredFormSet)
    if request.method == 'POST':
        recipe_form = AddNewRecipe(request.POST)
        ingredient_formset = new_recipe_formset(request.POST, request.FILES)

        if recipe_form.is_valid() and ingredient_formset.is_valid():
            recipe = Recipe.objects.get(id=pk)
            recipe.description = recipe_form.cleaned_data["description"]
            recipe.name = recipe_form.cleaned_data["name"]
            recipe.yields = recipe_form.cleaned_data['yields']
            recipe.recipe_steps = recipe_form.cleaned_data['recipe_steps']
            recipe.global_access = recipe_form.cleaned_data["Available to everyone"]

            for items in recipe.ingredients.all():
                items.delete()
            recipe.save()

            for f in ingredient_formset:
                cat = f.cleaned_data['category_name']
                try:
                    category = Category.objects.filter(name=cat)[0]
                except:
                    category = Category(name=cat)
                    category.save()
                product = Product(name=f.cleaned_data['product_name'], category=category)
                product.save()

                unit = Unit.objects.get(abbreviation=f.cleaned_data['unit'])
                quantity = f.cleaned_data['quantity']
                ingredient_api_name = str(f.cleaned_data['quantity']) + '%20' + unit.abbreviation + '%20' + product.name
                req = urllib2.Request(
                    'https://api.edamam.com/api/nutrition-data?app_id=' + settings.EDAMAM_API_ID + '&app_key=' + settings.EDAMAM_API_KEY + '&ingr=' + ingredient_api_name,
                    None, {'user-agent': 'syncstream/vimeo'})
                opener = urllib2.build_opener()
                f = opener.open(req)
                jsonData = json.JSONDecoder('latin1').decode(f.read())

                calories = jsonData['calories']
                dietLabels = jsonData['dietLabels']
                healthLabels = jsonData['healthLabels']

                ingredient = Ingredient(product=product, quantity=quantity,
                                        unit=unit, calories=calories, dietLabels=dietLabels, healthLabels=healthLabels)
                ingredient.save()
                recipe.ingredients.add(ingredient)
                recipe.save()

            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.use_trello:
                remove_card_trello(recipe.card, user_profile.trello_key)
                add_card_trello('Recipe', recipe, recipe.name, recipe.description, recipe.ingredients,
                                user_profile.trello_key)
            messages.add_message(request, messages.SUCCESS, 'Your recipe was updated successfully')
            return HttpResponseRedirect('/recipe/' + str(recipe.id))
    else:
        recipe_form = AddNewRecipe()
        ingredient_formset = new_recipe_formset()
    recipe_form = AddNewRecipe(
        initial={'name': recipe.name, 'description': recipe.description, 'private': recipe.global_access,
                 'yields': recipe.yields, 'recipe_steps': recipe.recipe_steps,
                 'global_access': recipe.global_access})
    ingredient_formset = formset_factory(AddIngredient, extra=0, max_num=10, formset=RequiredFormSet)
    ingredients_list = recipe.ingredients.all()
    formset = ingredient_formset(
        initial=[{'product_name': item.product.name,
                  'category_name': Product.objects.filter(id=item.product.pk)[0].category,
                  'quantity': item.quantity,
                  'unit': item.unit} for item in ingredients_list])

    c = {'recipe_form': recipe_form,
         'formset_name': "Ingredients",
         'form_name': "Recipe",
         'view_name': "Edit recipe",
         'ingredient_formset': formset,
         }
    c.update(csrf(request))
    return render_to_response('create_formset.html', c, RequestContext(request))


class ShowAllRecipes(ListView):
    context_object_name = 'recipe'
    queryset = Recipe.objects.filter(global_access=False)
    queryset2 = Recipe.objects.filter(global_access=True)

    def get_context_data(self, **kwargs):
        queryset2 = Recipe.objects.filter(global_access=True)
        if self.request.user.is_authenticated():
            queryset = Recipe.objects.filter(user=self.request.user)
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset,
                'object_list2': queryset2
            }
            context.update(kwargs)
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list2': queryset2,
            }
            context.update(kwargs)
        return context


def show_recipe(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    try:
        recipe = Recipe.objects.get(id=pk)
        ingredients = recipe.ingredients.all()
        return render_to_response('recipe.html', locals(), RequestContext(request))
    except:
        return HttpResponse(status=404)


@login_required
def create_shopping_list(request):
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    new_shopping_list_formset = formset_factory(AddIngredient, max_num=10, formset=RequiredFormSet)
    if request.method == 'POST':
        shopping_list_form = AddNewShoppingList(request.POST)
        ingredient_formset = new_shopping_list_formset(request.POST, request.FILES)

        if shopping_list_form.is_valid() and ingredient_formset.is_valid():
            shopping_list = ShoppingList(user=request.user, name=shopping_list_form.cleaned_data["name"])
            shopping_list.save()

            for f in ingredient_formset:
                cat = f.cleaned_data['category_name']
                try:
                    category = Category.objects.filter(name=cat)[0]
                except:
                    category = Category(name=cat)
                    category.save()
                product = Product(name=f.cleaned_data['product_name'], category=category)
                product.save()

                unit = Unit.objects.get(abbreviation=f.cleaned_data['unit'])
                quantity = f.cleaned_data['quantity']

                ingredient_api_name = str(f.cleaned_data['quantity']) + '%20' + unit.abbreviation + '%20' + product.name
                req = urllib2.Request(
                    'https://api.edamam.com/api/nutrition-data?app_id=' + settings.EDAMAM_API_ID + '&app_key=' + settings.EDAMAM_API_KEY + '&ingr=' + ingredient_api_name,
                    None, {'user-agent': 'syncstream/vimeo'})
                opener = urllib2.build_opener()
                f = opener.open(req)
                jsonData = json.JSONDecoder('latin1').decode(f.read())

                calories = jsonData['calories']
                dietLabels = jsonData['dietLabels']
                healthLabels = jsonData['healthLabels']

                ingredient = Ingredient(product=product, quantity=quantity,
                                        unit=unit, calories=calories, dietLabels=dietLabels, healthLabels=healthLabels)
                ingredient.save()
                shopping_list.items.add(ingredient)
                shopping_list.save()

            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.use_trello:
                add_card_trello('Shopping List', shopping_list, shopping_list.name, '',
                                shopping_list.items, user_profile.trello_key)
            messages.add_message(request, messages.SUCCESS, 'Your shopping list was created successfully')
            return HttpResponseRedirect('/shopping_list/' + str(shopping_list.id))
    else:
        recipe_form = AddNewShoppingList()
        ingredient_formset = new_shopping_list_formset()

    recipe_form = AddNewShoppingList()
    c = {'recipe_form': recipe_form,
         'view_name': "Create shopping list",
         'formset_name': "Items",
         'form_name': "Shopping List",
         'ingredient_formset': ingredient_formset,
         }
    c.update(csrf(request))
    return render_to_response('create_formset.html', c, RequestContext(request))


class ShowShoppingLists(LoginRequiredMixin, ListView):
    context_object_name = 'shopping_list'
    queryset = ShoppingList.objects.all()

    def get_context_data(self, **kwargs):
        queryset = ShoppingList.objects.filter(user=self.request.user)
        context = {
            'paginator': None,
            'page_obj': None,
            'is_paginated': False,
            'object_list': queryset,
        }
        context.update(kwargs)
        return context


@login_required
def show_shopping_list(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    try:
        list = ShoppingList.objects.get(id=pk)
        items = list.items.all()
        name = "Shopping list"
        return render_to_response('list.html', locals(), RequestContext(request))
    except:
        return HttpResponse(status=404)


@login_required
def delete_shopping_list(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    shopping_list = ShoppingList.objects.get(id=pk)
    for items in shopping_list.items.all():
        items.delete()
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.use_trello:
        card_id = shopping_list.card
        remove_card_trello(card_id, user_profile.trello_key)
    shopping_list.delete()
    messages.add_message(request, messages.SUCCESS, 'Your shopping list was removed successfully')
    return HttpResponseRedirect('/shopping_lists/')


@login_required
def edit_shopping_list(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    shopping_list = ShoppingList.objects.get(id=pk)

    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    new_shopping_list_formset = formset_factory(AddIngredient, max_num=10, formset=RequiredFormSet)
    if request.method == 'POST':
        shopping_list_form = AddNewShoppingList(request.POST)
        ingredient_formset = new_shopping_list_formset(request.POST, request.FILES)

        if shopping_list_form.is_valid() and ingredient_formset.is_valid():
            shopping_list = ShoppingList.objects.get(id=pk)
            shopping_list.name = shopping_list_form.cleaned_data["name"]
            for items in shopping_list.items.all():
                items.delete()
            shopping_list.save()

            for f in ingredient_formset:
                cat = f.cleaned_data['category_name']
                try:
                    category = Category.objects.filter(name=cat)[0]
                except:
                    category = Category(name=cat)
                    category.save()
                product = Product(name=f.cleaned_data['product_name'], category=category)
                product.save()

                unit = Unit.objects.get(abbreviation=f.cleaned_data['unit'])
                quantity = f.cleaned_data['quantity']

                ingredient_api_name = str(f.cleaned_data['quantity']) + '%20' + unit.abbreviation + '%20' + product.name
                req = urllib2.Request(
                    'https://api.edamam.com/api/nutrition-data?app_id=' + settings.EDAMAM_API_ID + '&app_key=' + settings.EDAMAM_API_KEY + '&ingr=' + ingredient_api_name,
                    None, {'user-agent': 'syncstream/vimeo'})
                opener = urllib2.build_opener()
                f = opener.open(req)
                jsonData = json.JSONDecoder('latin1').decode(f.read())

                calories = jsonData['calories']
                dietLabels = jsonData['dietLabels']
                healthLabels = jsonData['healthLabels']

                ingredient = Ingredient(product=product, quantity=quantity,
                                        unit=unit, calories=calories, dietLabels=dietLabels, healthLabels=healthLabels)
                ingredient.save()
                shopping_list.items.add(ingredient)
                shopping_list.save()

            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.use_trello:
                remove_card_trello(shopping_list.card, user_profile.trello_key)
                add_card_trello('Shopping List', shopping_list, shopping_list.name, '',
                                shopping_list.items, user_profile.trello_key)
            messages.add_message(request, messages.SUCCESS, 'Your shopping list was updated successfully')
            return HttpResponseRedirect('/shopping_list/' + str(shopping_list.id))
    recipe_form = AddNewShoppingList(initial={'name': shopping_list.name})
    ingredient_formset = formset_factory(AddIngredient, extra=0, max_num=10, formset=RequiredFormSet)
    ingredients_list = shopping_list.items.all()
    formset = ingredient_formset(
        initial=[{'product_name': item.product.name,
                  'category_name': Product.objects.filter(id=item.product.pk)[0].category,
                  'quantity': item.quantity,
                  'unit': item.unit} for item in ingredients_list])

    c = {'recipe_form': recipe_form,
         'view_name': "Edit shopping list",
         'formset_name': "Items",
         'form_name': "Shopping List",
         'ingredient_formset': formset,
         }
    c.update(csrf(request))
    return render_to_response('create_formset.html', c, RequestContext(request))


@login_required
def create_product_list(request):
    if request.method == 'POST':
        form = AddNewProduct(request.POST, user=request.user)
        if form.is_valid():
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                category = form.cleaned_data['category']
                try:
                    category = Category.objects.filter(name=category)[0]
                except:
                    category = Category(name=category)
                    category.save()

                name = form.cleaned_data['name']
                product = Product(name=name, category=category)
                product.save()

                barcode = form.cleaned_data['barcode']
                manufacturer = form.cleaned_data['manufacturer']
                quantity_in_box = form.cleaned_data['quantity_in_box']
                product_details = ProductDetails(product=product, barcode=barcode, manufacturer=manufacturer,
                                                 quantity=quantity_in_box)
                product_details.save()
                quantity = form.cleaned_data['quantity']
                productList = ProductList(user=request.user, quantity=quantity, items=product_details)
                productList.save()

                if user_profile.use_trello:
                    add_card_trello('Product', productList, productList.items.product.name,
                                    productList.items.product.category.name,
                                    '', user_profile.trello_key)
            except Exception as e:
                error = e
                return render_to_response('create_product.html', locals(), RequestContext(request))
        else:
            return render_to_response('create_product.html', locals(), RequestContext(request))
        messages.add_message(request, messages.SUCCESS, 'Your product was added successfully')
        return HttpResponseRedirect('/product/' + str(productList.id))

    else:
        form = AddNewProduct(user=request.user)

    return render(request, 'create_product.html', {
        'form': form,
        'name': 'Create Product'
    })


class ShowProductLists(LoginRequiredMixin, ListView):
    context_object_name = 'product_list'
    queryset = ProductList.objects.all()

    def get_context_data(self, **kwargs):
        queryset = ProductList.objects.filter(user=self.request.user)
        context = {
            'paginator': None,
            'page_obj': None,
            'is_paginated': False,
            'object_list': queryset,
        }
        context.update(kwargs)
        return context


@login_required
def show_product_list(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    try:
        list = ProductList.objects.get(id=pk)
        name = "Product"
        return render_to_response('product.html', locals(), RequestContext(request))
    except:
        return HttpResponse(status=404)


@login_required
def delete_product_list(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    product_list = ProductList.objects.get(id=pk)
    product_list.delete()
    messages.add_message(request, messages.SUCCESS, 'Your product was removed successfully')
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.use_trello:
        card_id = product_list.card
        remove_card_trello(card_id, user_profile.trello_key)
    return HttpResponseRedirect('/')


@login_required
def edit_product_list(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    productList = ProductList.objects.get(id=pk)
    if request.method == 'POST':
        form = AddNewProduct(request.POST)
        if form.is_valid():
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                category = form.cleaned_data['category']
                try:
                    category = Category.objects.filter(name=category)[0]
                except:
                    category = Category(name=category)
                    category.save()

                name = form.cleaned_data['name']
                asd = ProductList.items
                product_details = ProductDetails.objects.get(id=productList.items_id)

                product = Product.objects.get(id=product_details.product.id)
                product.name = name
                product.category = category
                product.save()

                product_details.barcode = form.cleaned_data['barcode']
                product_details.manufacturer = form.cleaned_data['manufacturer']
                product_details.quantity = form.cleaned_data['quantity_in_box']
                product_details.save()

                productList.quantity = form.cleaned_data['quantity']
                productList.save()
                if user_profile.use_trello:
                    remove_card_trello(productList.card, user_profile.trello_key)
                    add_card_trello('Product', productList, productList.items.product.name,
                                    productList.items.product.category.name,
                                    '', user_profile.trello_key)
            except Exception as e:
                error = e
                return render_to_response('edit_product.html', locals(), RequestContext(request))
        else:
            return render_to_response('edit_product.html', locals(), RequestContext(request))
        messages.add_message(request, messages.SUCCESS, 'Your product was updated successfully')
        return HttpResponseRedirect('/product/' + str(productList.id))
    else:
        form = AddNewProduct(initial={'quantity': productList.quantity, 'barcode': productList.items.barcode,
                                      'manufacturer': productList.items.manufacturer,
                                      'quantity_in_box': productList.items.quantity,
                                      'category': productList.items.product.category.name,
                                      'name': productList.items.product.name})

    return render(request, 'edit_product.html', {
        'form': form,
        'id': pk,
        'name': 'Edit Product'
    })


SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Przepisy'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'przepisy.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        flags = tools.argparser.parse_args(args=[])
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def add_event(name, meal, recipe, date, time):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    start_time_of_meal = str(date) + 'T' + str(time) + '-00:00'
    end_time = datetime.time(time.hour + 1, time.minute, 0)
    end_time_of_meal = str(date) + 'T' + str(end_time) + '-00:00'
    event = {
        'summary': 'Dinner: ' + name,
        'description': recipe.description,
        'start': {'dateTime': start_time_of_meal},
        'end': {'dateTime': end_time_of_meal},
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    meal.event = str(event['id'])
    meal.save()


def update_event(event_id, recipe, date, time):
    try:
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        event['summary'] = 'Dinner: ' + recipe.name
        event['description'] = recipe.description
        start_time_of_meal = str(date) + 'T' + str(time) + '-00:00'
        end_time = datetime.time(time.hour + 1, time.minute, 0)
        end_time_of_meal = str(date) + 'T' + str(end_time) + '-00:00'
        event['start'] = {'dateTime': start_time_of_meal},
        event['end'] = {'dateTime': end_time_of_meal},
        service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    except:
        return HttpResponse('Event with that id doesnt exist in google calendar')


def delete_event(event_id):
    try:
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        service.events().delete(calendarId='primary', eventId=event_id).execute()
    except:
        return HttpResponse('Event with that id doesnt exist in google calendar')


def add_card_trello(value, object, name, description, items, token):
    client = TrelloClient(api_key=settings.TRELLO_APP_KEY, token=token)
    board_id = client.list_boards()[1].id
    lists = client.get_board(board_id).all_lists()
    if value == 'Recipe':
        for list in lists:
            if list.name == 'Recipes':
                card = list.add_card(name, description)
                items_to_add = []
                for i in items.all():
                    items_to_add.append(str(i.quantity) + 'x ' + i.unit.abbreviation + ' ' + i.product.name)
                card.add_checklist('Ingredients', items_to_add)
                object.card = card.id
                object.save()
    elif value == 'Shopping List':
        for list in lists:
            if list.name == 'Shopping Lists':
                card = list.add_card(name)
                items_to_add = []
                for i in items.all():
                    items_to_add.append(str(i.quantity) + 'x ' + i.unit.abbreviation + ' ' + i.product.name)
                card.add_checklist('Products to buy', items_to_add)
                object.card = card.id
                object.save()
    elif value == 'Product':
        for list in lists:
            if list.name == 'Product Lists':
                card = list.add_card(name, description + ' ' + str(object.quantity))
                object.card = card.id
                object.save()


def remove_card_trello(card_id, token):
    try:
        client = TrelloClient(api_key=settings.TRELLO_APP_KEY, token=token)
        client.get_card(card_id).delete()
    except:
        return HttpResponse('Card with that id doesnt exist.')


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('full_name', 'abbreviation')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)

    class Meta:
        model = Product
        fields = ('name', 'category')


class ProductDetailsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = ProductDetails
        fields = ('product', 'barcode', 'manufacturer', 'quantity')


class IngredientSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    unit = UnitSerializer(many=False)

    class Meta:
        model = Ingredient
        fields = ('product', 'quantity', 'unit', 'calories', 'dietLabels', 'healthLabels')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('name', 'description', 'recipe_steps', 'ingredients', 'yields', 'date')


class MealSerializer(serializers.ModelSerializer):
    name = RecipeSerializer(many=False, read_only=True)

    class Meta:
        model = Meal
        fields = ('name', 'yields', 'date', 'time')


class ShoppingListSerializer(serializers.ModelSerializer):
    items = IngredientSerializer(many=True)

    class Meta:
        model = ShoppingList
        fields = ('name', 'items')


class ProductListSerializer(serializers.ModelSerializer):
    items = ProductDetailsSerializer(many=False)

    class Meta:
        model = ProductList
        fields = ('quantity', 'items')


@api_view(['GET'])
def own_recipe_list(request):
    if request.method == 'GET':
        recipes = Recipe.objects.filter(user=request.user)
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def recipe_list(request):
    if request.method == 'GET':
        recipes = Recipe.objects.filter(global_access=True)
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        new_recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            ing = Ingredient.objects.create(**ingredient)
            new_recipe.ingredients.add(ing)
        return new_recipe

    def update(self, instance, validated_data):
        new_recipe = instance[0]
        new_recipe.name = validated_data.get('name')
        new_recipe.description = validated_data.get('description')
        ingredients = validated_data.get('ingredients')
        for items in new_recipe.ingredients.all():
            items.delete()
        for ingredient in ingredients:
            ing = Ingredient.objects.create(**ingredient)
            new_recipe.ingredients.add(ing)
        new_recipe.save()
        return new_recipe


@api_view(['POST'])
def post_recipe(request):
    if request.method == 'POST':
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            recipe = Recipe(user=request.user, description=request.data["description"],
                            name=request.data["name"], yields=request.data['yields'],
                            recipe_steps=request.data['recipe_steps'])
            recipe.save()
            for ingredient in request.data['ingredients']:
                cat = ingredient['product']['category']['name']
                try:
                    category = Category.objects.filter(name=cat)[0]
                except:
                    category = Category(name=cat)
                    category.save()

                product = Product(name=ingredient['product']['name'], category=category)
                product.save()
                unit = Unit.objects.get(abbreviation=ingredient['unit']['abbreviation'])
                quantity = ingredient['quantity']

                ingredient_api_name = str(ingredient['quantity']) + '%20' + unit.abbreviation + '%20' + product.name
                req = urllib2.Request(
                    'https://api.edamam.com/api/nutrition-data?app_id=' + settings.EDAMAM_API_ID + '&app_key=' + settings.EDAMAM_API_KEY + '&ingr=' + ingredient_api_name,
                    None, {'user-agent': 'syncstream/vimeo'})
                opener = urllib2.build_opener()
                f = opener.open(req)
                jsonData = json.JSONDecoder('latin1').decode(f.read())

                calories = jsonData['calories']
                dietLabels = jsonData['dietLabels']
                healthLabels = jsonData['healthLabels']

                ingredient = Ingredient(product=product, quantity=quantity,
                                        unit=unit, calories=calories, dietLabels=dietLabels, healthLabels=healthLabels)
                ingredient.save()
                recipe.ingredients.add(ingredient)
                recipe.save()
                user_profile = UserProfile.objects.get(user=request.user)
                if user_profile.use_trello:
                    add_card_trello('Recipe', recipe, recipe.name, recipe.description, recipe.ingredients,
                                    user_profile.trello_key)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def recipe(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    if request.method == 'GET':
        new_recipe = Recipe.objects.filter(id=pk)
        if (new_recipe.__len__() > 0) and (new_recipe[0].user == request.user):
            serializer = RecipeSerializer(new_recipe, many=True)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'PUT':
        recipe = Recipe.objects.filter(id=pk)
        if recipe.__len__() > 0:
            serializer = RecipeSerializer(recipe, data=request.data)
            if serializer.is_valid() and (recipe[0].user == request.user):
                new_recipe = recipe[0]
                new_recipe.description = request.data["description"]
                new_recipe.name = request.data["name"]
                new_recipe.yields = request.data['yields']
                new_recipe.recipe_steps = request.data['recipe_steps']
                for items in new_recipe.ingredients.all():
                    items.delete()
                new_recipe.save()

                for ingredient in request.data['ingredients']:
                    cat = ingredient['product']['category']['name']
                    try:
                        category = Category.objects.filter(name=cat)[0]
                    except:
                        category = Category(name=cat)
                        category.save()

                    product = Product(name=ingredient['product']['name'], category=category)
                    product.save()
                    unit = Unit.objects.get(abbreviation=ingredient['unit']['abbreviation'])
                    quantity = ingredient['quantity']

                    ingredient_api_name = str(ingredient['quantity']) + '%20' + unit.abbreviation + '%20' + product.name
                    req = urllib2.Request(
                        'https://api.edamam.com/api/nutrition-data?app_id=' + settings.EDAMAM_API_ID + '&app_key=' + settings.EDAMAM_API_KEY + '&ingr=' + ingredient_api_name,
                        None, {'user-agent': 'syncstream/vimeo'})
                    opener = urllib2.build_opener()
                    f = opener.open(req)
                    jsonData = json.JSONDecoder('latin1').decode(f.read())

                    calories = jsonData['calories']
                    dietLabels = jsonData['dietLabels']
                    healthLabels = jsonData['healthLabels']

                    ingredient = Ingredient(product=product, quantity=quantity,
                                            unit=unit, calories=calories, dietLabels=dietLabels, healthLabels=healthLabels)
                    ingredient.save()
                    new_recipe.ingredients.add(ingredient)
                    new_recipe.save()
                    user_profile = UserProfile.objects.get(user=request.user)
                    if user_profile.use_trello:
                        remove_card_trello(new_recipe.card, user_profile.trello_key)
                        add_card_trello('Recipe', new_recipe, recipe.name, new_recipe.description, new_recipe.ingredients,
                                        user_profile.trello_key)
                return Response(serializer.initial_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        new_recipe = Recipe.objects.filter(id=pk)
        if (new_recipe.__len__() > 0) and (new_recipe[0].user == request.user):
            for items in new_recipe[0].ingredients.all():
                items.delete()
            new_recipe.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def meal_list(request):
    if request.method == 'GET':
        meals = Meal.objects.filter(user=request.user)
        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def shopping_list_list(request):
    if request.method == 'GET':
        shopping_list = ShoppingList.objects.filter(user=request.user)
        serializer = ShoppingListSerializer(shopping_list, many=True)
        return Response(serializer.data)
    else:
        Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def product_list_list(request):
    if request.method == 'GET':
        product_list = ProductList.objects.filter(user=request.user)
        serializer = ProductListSerializer(product_list, many=True)
        return Response(serializer.data)
    else:
        Response(status=status.HTTP_401_UNAUTHORIZED)
