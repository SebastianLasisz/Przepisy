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
            calories = 5
            dietLabels = 5
            healthLabels = 5
            recipe = Recipe(user=request.user, description=recipe_form.cleaned_data["description"],
                            name=recipe_form.cleaned_data["name"], yields=recipe_form.cleaned_data['yields'],
                            recipe_steps=recipe_form.cleaned_data['recipe_steps'], calories=calories,
                            dietLabels=dietLabels, healthLabels=healthLabels,
                            global_access=recipe_form.cleaned_data["Available to everyone"])
            recipe.save()
            for f in ingredient_formset:
                cat = f.cleaned_data['category_name']
                try:
                    category = Category.objects.filter(name=cat)[0]
                except:
                    category = Category(name=cat)
                    category.save()
                product = Product(name=f.cleaned_data['product_name'])
                product.save()
                product.category.add(category)

                product.save()

                unit = Unit.objects.get(abbreviation=f.cleaned_data['unit'])
                ingredient = Ingredient(product=product, quantity=f.cleaned_data['quantity'],
                                        unit=unit)
                ingredient.save()
                recipe.ingredients.add(ingredient)
                recipe.save()
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.use_trello:
                add_card_trello('Recipe', recipe, recipe.name, recipe.description, recipe.ingredients)
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
        remove_card_trello(card_id)
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
                product = Product(name=f.cleaned_data['product_name'])
                product.save()
                product.category.add(category)

                product.save()

                unit = Unit.objects.get(abbreviation=f.cleaned_data['unit'])
                ingredient = Ingredient(product=product, quantity=f.cleaned_data['quantity'],
                                        unit=unit)
                ingredient.save()
                recipe.ingredients.add(ingredient)
                recipe.save()

            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.use_trello:
                remove_card_trello(recipe.card)
                add_card_trello('Recipe', recipe, recipe.name, recipe.description, recipe.ingredients)
            messages.add_message(request, messages.SUCCESS, 'Your recipe was updated successfully')
            return HttpResponseRedirect('/recipe/' + str(recipe.id))
    else:
        recipe_form = AddNewRecipe()
        ingredient_formset = new_recipe_formset()
    recipe_form = AddNewRecipe(
        initial={'name': recipe.name, 'description': recipe.description, 'private': recipe.global_access,
                 'yields': recipe.yields, 'recipe_steps': recipe.recipe_steps, 'calories': recipe.calories,
                 'dietLabels': recipe.dietLabels, 'healthLabels': recipe.healthLabels,
                 'global_access': recipe.global_access})
    ingredient_formset = formset_factory(AddIngredient, extra=0, max_num=10, formset=RequiredFormSet)
    ingredients_list = recipe.ingredients.all()
    formset = ingredient_formset(
        initial=[{'product_name': item.product.name,
                  'category_name': Product.objects.filter(id=item.product.pk)[0].category.all()[0],
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
                product = Product(name=f.cleaned_data['product_name'])
                product.save()
                product.category.add(category)
                product.save()

                unit = Unit.objects.get(abbreviation=f.cleaned_data['unit'])
                ingredient = Ingredient(product=product, quantity=f.cleaned_data['quantity'],
                                        unit=unit)
                ingredient.save()
                shopping_list.items.add(ingredient)
                shopping_list.save()

            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.use_trello:
                add_card_trello('Shopping List', shopping_list, shopping_list.name, shopping_list.description,
                                shopping_list.items)
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
        remove_card_trello(card_id)
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
                product = Product(name=f.cleaned_data['product_name'])
                product.save()
                product.category.add(category)
                product.save()

                unit = Unit.objects.get(abbreviation=f.cleaned_data['unit'])
                ingredient = Ingredient(product=product, quantity=f.cleaned_data['quantity'],
                                        unit=unit)
                ingredient.save()
                shopping_list.items.add(ingredient)
                shopping_list.save()

            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.use_trello:
                remove_card_trello(shopping_list.card)
                add_card_trello('Shopping List', shopping_list, shopping_list.name, shopping_list.description,
                                shopping_list.items)
            messages.add_message(request, messages.SUCCESS, 'Your shopping list was updated successfully')
            return HttpResponseRedirect('/shopping_list/' + str(shopping_list.id))
    recipe_form = AddNewShoppingList(initial={'name': shopping_list.name})
    ingredient_formset = formset_factory(AddIngredient, extra=0, max_num=10, formset=RequiredFormSet)
    ingredients_list = shopping_list.items.all()
    formset = ingredient_formset(
        initial=[{'product_name': item.product.name,
                  'category_name': Product.objects.filter(id=item.product.pk)[0].category.all()[0],
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
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    new_product_list_formset = formset_factory(AddIngredient, max_num=10, formset=RequiredFormSet)
    if request.method == 'POST':
        product_list_form = AddNewProductList(request.POST)
        ingredient_formset = new_product_list_formset(request.POST, request.FILES)

        if product_list_form.is_valid() and ingredient_formset.is_valid():
            product_list = ProductList(user=request.user, description=product_list_form.cleaned_data["description"],
                                       name=product_list_form.cleaned_data["name"])
            product_list.save()
            for f in ingredient_formset:
                ingredient = Ingredient(unit=f.cleaned_data['unit'], name=f.cleaned_data['name'],
                                        value=f.cleaned_data['value'])
                ingredient.save()
                product_list.items.add(ingredient)
                product_list.save()
            add_card_trello('Product List', product_list, product_list.name, product_list.description,
                            product_list.items)
            return HttpResponseRedirect('/')
    else:
        recipe_form = AddNewProductList()
        ingredient_formset = new_product_list_formset()

    c = {'recipe_form': recipe_form,
         'view_name': "Create product list",
         'formset_name': "Items",
         'form_name': "Product List",
         'ingredient_formset': ingredient_formset,
         }
    c.update(csrf(request))
    return render_to_response('create_formset.html', c, RequestContext(request))


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
        items = list.items.all()
        name = "Product list"
        return render_to_response('list.html', locals(), RequestContext(request))
    except:
        return HttpResponse(status=404)


@login_required
def delete_product_list(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    product_list = ProductList.objects.get(id=pk)
    for items in product_list.items.all():
        items.delete()
    card_id = product_list.card
    product_list.delete()
    remove_card_trello(card_id)
    return HttpResponseRedirect('/')


@login_required
def edit_product_list(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    product_list = ProductList.objects.get(id=pk)

    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    new_product_list_formset = formset_factory(AddIngredient, max_num=10, formset=RequiredFormSet)
    if request.method == 'POST':
        product_list_form = AddNewProductList(request.POST)
        ingredient_formset = new_product_list_formset(request.POST, request.FILES)

        if product_list_form.is_valid() and ingredient_formset.is_valid():
            product_list = ProductList.objects.get(id=pk)
            product_list.description = product_list_form.cleaned_data["description"]
            product_list.name = product_list_form.cleaned_data["name"]
            for items in product_list.items.all():
                items.delete()
            product_list.save()

            for f in ingredient_formset:
                ingredient = Ingredient(unit=f.cleaned_data['unit'], name=f.cleaned_data['name'],
                                        value=f.cleaned_data['value'])
                ingredient.save()
                product_list.items.add(ingredient)
                product_list.save()
            remove_card_trello(product_list.card)
            add_card_trello('Product List', product_list, product_list.name, product_list.description,
                            product_list.items)
            return HttpResponseRedirect('/')
    recipe_form = AddNewProductList(
        initial={'name': product_list.name, 'description': product_list.description})
    ingredient_formset = formset_factory(AddIngredient, extra=0, max_num=10, formset=RequiredFormSet)
    ingredients_list = product_list.items.all()
    formset = ingredient_formset(
        initial=[{'name': item.name, 'value': item.value, 'unit': item.unit} for item in ingredients_list])

    c = {'recipe_form': recipe_form,
         'view_name': "Edit product list",
         'formset_name': "Items",
         'form_name': "Product List",
         'ingredient_formset': formset,
         }
    c.update(csrf(request))
    return render_to_response('create_formset.html', c, RequestContext(request))


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


def add_card_trello(value, object, name, description, items):
    client = TrelloClient(api_key=settings.TRELLO_APP_KEY, token=settings.TRELLO_API_TOKEN)
    board_id = client.list_boards()[1].id
    lists = client.get_board(board_id).all_lists()
    if value == 'Recipe':
        for list in lists:
            if list.name == 'Recipes':
                card = list.add_card(name, description)
                items_to_add = []
                for i in items.all():
                    items_to_add.append(str(i.value) + 'x ' + i.unit + ' ' + i.name)
                card.add_checklist('Ingredients', items_to_add)
                object.card = card.id
                object.save()
    elif value == 'Shopping List':
        for list in lists:
            if list.name == 'Shopping Lists':
                card = list.add_card(name, description)
                items_to_add = []
                for i in items.all():
                    items_to_add.append(str(i.value) + 'x ' + i.unit + ' ' + i.name)
                card.add_checklist('Products to buy', items_to_add)
                object.card = card.id
                object.save()
    elif value == 'Product List':
        for list in lists:
            if list.name == 'Product Lists':
                card = list.add_card(name, description)
                items_to_add = []
                for i in items.all():
                    items_to_add.append(str(i.value) + 'x ' + i.unit + ' ' + i.name)
                card.add_checklist('Products you own', items_to_add)
                object.card = card.id
                object.save()


def remove_card_trello(card_id):
    try:
        client = TrelloClient(api_key=settings.TRELLO_APP_KEY, token=settings.TRELLO_API_TOKEN)
        client.get_card(card_id).delete()
    except:
        return HttpResponse('Card with that id doesnt exist.')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'value', 'unit')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('name', 'description', 'ingredients', 'date')

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


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ('name', 'date', 'time')


class ShoppingListSerializer(serializers.ModelSerializer):
    items = IngredientSerializer(many=True)

    class Meta:
        model = ShoppingList
        fields = ('name', 'description', 'items')

    def create(self, validated_data):
        items = validated_data.pop('items')
        new_shopping_list = ShoppingList.objects.create(**validated_data)
        for item in items:
            ing = Ingredient.objects.create(**item)
            new_shopping_list.items.add(ing)
        return new_shopping_list

    def update(self, instance, validated_data):
        new_shopping_list = instance[0]
        new_shopping_list.name = validated_data.get('name')
        new_shopping_list.description = validated_data.get('description')
        items = validated_data.get('items')
        for items in new_shopping_list.items.all():
            items.delete()
        for item in items:
            ing = Ingredient.objects.create(**item)
            new_shopping_list.items.add(ing)
        new_shopping_list.save()
        return new_shopping_list


class ProductListSerializer(serializers.ModelSerializer):
    items = IngredientSerializer(many=True)

    class Meta:
        model = ProductList
        fields = ('name', 'description', 'items')

    def create(self, validated_data):
        items = validated_data.pop('items')
        new_product_list = ProductList.objects.create(**validated_data)
        for item in items:
            ing = Ingredient.objects.create(**item)
            new_product_list.items.add(ing)
        return new_product_list

    def update(self, instance, validated_data):
        new_product_list = instance[0]
        new_product_list.name = validated_data.get('name')
        new_product_list.description = validated_data.get('description')
        items = validated_data.get('items')
        for items in new_product_list.items.all():
            items.delete()
        for item in items:
            ing = Ingredient.objects.create(**item)
            new_product_list.items.add(ing)
        new_product_list.save()
        return new_product_list


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


@api_view(['POST'])
def post_recipe(request):
    if request.method == 'POST':
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def recipe(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    if request.method == 'GET':
        new_recipe = Recipe.objects.filter(id=pk)
        if (new_recipe.__len__() > 0) and (new_recipe[0].user == request.user):
            serializer = RecipeSerializer(new_recipe, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'PUT':
        new_recipe = Recipe.objects.filter(id=pk)
        if new_recipe.__len__() > 0:
            serializer = RecipeSerializer(new_recipe, data=request.data)
            if serializer.is_valid() and (new_recipe[0].user == request.user):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        new_recipe = Recipe.objects.filter(id=pk)
        if (new_recipe.__len__() > 0) and (new_recipe[0].user == request.user):
            for items in new_recipe[0].ingredients.all():
                items.delete()
            new_recipe.delete()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def shopping_list_list(request):
    if request.method == 'GET':
        shopping_list = ShoppingList.objects.filter(user=request.user)
        serializer = ShoppingListSerializer(shopping_list, many=True)
        return Response(serializer.data)
    else:
        Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def post_shopping_list(request):
    if request.method == 'POST':
        serializer = ShoppingListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT', 'DELETE'])
def shopping_list(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    if request.method == 'GET':
        new_shopping_list = ShoppingList.objects.filter(id=pk)
        if (new_shopping_list.__len__() > 0) and (new_shopping_list[0].user == request.user):
            serializer = ShoppingListSerializer(new_shopping_list, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'PUT':
        new_shopping_list = ShoppingList.objects.filter(id=pk)
        if new_shopping_list.__len__() > 0:
            serializer = ShoppingListSerializer(new_shopping_list, data=request.data)
            if serializer.is_valid() and (new_shopping_list[0].user == request.user):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        new_shopping_list = ShoppingList.objects.filter(id=pk)
        if (new_shopping_list.__len__() > 0) and (new_shopping_list[0].user == request.user):
            for item in new_shopping_list[0].items.all():
                item.delete()
            new_shopping_list.delete()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
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


@api_view(['POST'])
def post_product_list(request):
    if request.method == 'POST':
        serializer = ProductListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT', 'DELETE'])
def product_list(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    if request.method == 'GET':
        new_product_list = ProductList.objects.filter(id=pk)
        if (new_product_list.__len__() > 0) and (new_product_list[0].user == request.user):
            serializer = ProductListSerializer(new_product_list, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'PUT':
        new_product_list = ProductList.objects.filter(id=pk)
        if new_product_list.__len__() > 0:
            serializer = ProductListSerializer(new_product_list, data=request.data)
            if serializer.is_valid() and (new_product_list[0].user == request.user):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        new_product_list = ProductList.objects.filter(id=pk)
        if (new_product_list.__len__() > 0) and (new_product_list[0].user == request.user):
            for item in new_product_list[0].items.all():
                item.delete()
            new_product_list.delete()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
        Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def meal_list(request):
    if request.method == 'GET':
        meals = Meal.objects.filter(user=request.user)
        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def post_meal(request):
    if request.method == 'POST':
        serializer = MealSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def meal(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    if request.method == 'GET':
        new_meal = Meal.objects.filter(id=pk)
        if (new_meal.__len__() > 0) and (new_meal[0].user == request.user):
            serializer = MealSerializer(new_meal, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'PUT':
        new_meal = Meal.objects.filter(id=pk)
        if new_meal.__len__() > 0:
            serializer = MealSerializer(new_meal[0], data=request.data)
            if serializer.is_valid() and (new_meal[0].user == request.user):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        new_meal = Meal.objects.filter(id=pk)
        if (new_meal.__len__() > 0) and (new_meal[0].user == request.user):
            new_meal.delete()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
        Response(status=status.HTTP_401_UNAUTHORIZED)

        # http://pastebin.com/7p2McnXZ
