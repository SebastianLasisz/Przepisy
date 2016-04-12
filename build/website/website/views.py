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
                return render_to_response('index.html', locals(), RequestContext(request))
        else:
            return render_to_response('index.html', locals(), RequestContext(request))
    else:
        return render_to_response('login.html', locals(), RequestContext(request))


@login_required
def logout_view(request):
    logout(request)
    return render_to_response('index.html', locals(), RequestContext(request))


def register(request):
    if request.method == 'POST':
        form = RegisterNewUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            repeat_password = form.cleaned_data['repeat_password']
            r = User(username=username,
                     email=email,
                     password=make_password(password))
            try:
                r.save()
                us = UserProfile(user=r, avatar="/pic_folder/logo3.jpg", signature="")
                us.save()
                shopping_list = ShoppingList(name='Default shopping list', user=r)
                shopping_list.save()
                product_list = ProductList(name='Default product list', user=r)
                product_list.save()
            except:
                error = "That user name is already taken"
                return render_to_response('register.html', locals(), RequestContext(request))
        else:
            return render_to_response('register.html', locals(), RequestContext(request))
        return render_to_response('index.html', locals(), RequestContext(request))
    else:
        form = RegisterNewUserForm()

    return render(request, 'register.html', {
        'form': form
    })


@login_required
def create_meal(request):
    if request.method == 'POST':
        form = AddNewMeal(request.POST)
        if form.is_valid():
            try:
                name = form.cleaned_data['name']
                recipe = Recipe.objects.filter(name=name)[0]
                date = form.cleaned_data['date']
                time = form.cleaned_data['time']
                meal = Meal(user=request.user, name=recipe, date=date, time=time)
                meal.save()
            except:
                error = "That recipe doesn't exist"
                return render_to_response('create.html', locals(), RequestContext(request))
        else:
            return render_to_response('create.html', locals(), RequestContext(request))
        return render_to_response('index.html', locals(), RequestContext(request))
    else:
        form = AddNewMeal()

    return render(request, 'create.html', {
        'form': form,
        'name': 'Create Meal'
    })


@login_required
def edit_meal(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    meal = Meal.objects.get(id=pk)
    if request.method == 'POST':
        form = AddNewMeal(request.POST)
        if form.is_valid():
            try:
                name = form.cleaned_data['name']
                meal.name = Recipe.objects.filter(name=name)[0]
                meal.date = form.cleaned_data['date']
                meal.time = form.cleaned_data['time']
                meal.save()
            except:
                error = "That recipe doesn't exist"
                return render_to_response('create.html', locals(), RequestContext(request))
        else:
            return render_to_response('create.html', locals(), RequestContext(request))
        return render_to_response('index.html', locals(), RequestContext(request))
    else:
        form = AddNewMeal(initial={'name': meal.name, 'date': meal.date, 'time': meal.time})

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
    pk = int(kwargs.get('pk', None))
    meal = Meal.objects.get(id=pk)
    meal.delete()
    return render_to_response('index.html', locals(), RequestContext(request))


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
        ingredient_formset = new_recipe_formset(request.POST, request.FILES)

        if recipe_form.is_valid() and ingredient_formset.is_valid():
            recipe = Recipe(user=request.user, description=recipe_form.cleaned_data["description"],
                            name=recipe_form.cleaned_data["name"], global_access=recipe_form.cleaned_data["private"])
            recipe.save()
            for f in ingredient_formset:
                ingredient = Ingredient(unit=f.cleaned_data['unit'], name=f.cleaned_data['name'],
                                        value=f.cleaned_data['value'])
                ingredient.save()
                recipe.ingredients.add(ingredient)
                recipe.save()
            return render_to_response('index.html', locals(), RequestContext(request))
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
    for items in recipe.ingredients.all():
        items.delete()
    recipe.delete()
    return render_to_response('index.html', locals(), RequestContext(request))


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
            recipe.global_access = recipe_form.cleaned_data["private"]
            for items in recipe.ingredients.all():
                items.delete()
            recipe.save()

            for f in ingredient_formset:
                ingredient = Ingredient(unit=f.cleaned_data['unit'], name=f.cleaned_data['name'],
                                        value=f.cleaned_data['value'])
                ingredient.save()
                recipe.ingredients.add(ingredient)
                recipe.save()
            return render_to_response('index.html', locals(), RequestContext(request))
    else:
        recipe_form = AddNewRecipe()
        ingredient_formset = new_recipe_formset()
    recipe_form = AddNewRecipe(
        initial={'name': recipe.name, 'description': recipe.description, 'private': recipe.global_access})
    ingredient_formset = formset_factory(AddIngredient, extra=0, max_num=10, formset=RequiredFormSet)
    ingredients_list = recipe.ingredients.all()
    formset = ingredient_formset(
        initial=[{'name': item.name, 'value': item.value, 'unit': item.unit} for item in ingredients_list])

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
                'object_list': queryset2,
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
            shopping_list = ShoppingList(user=request.user, description=shopping_list_form.cleaned_data["description"],
                                         name=shopping_list_form.cleaned_data["name"])
            shopping_list.save()
            for f in ingredient_formset:
                ingredient = Ingredient(unit=f.cleaned_data['unit'], name=f.cleaned_data['name'],
                                        value=f.cleaned_data['value'])
                ingredient.save()
                shopping_list.items.add(ingredient)
                shopping_list.save()
            return render_to_response('index.html', locals(), RequestContext(request))
    else:
        recipe_form = AddNewShoppingList()
        ingredient_formset = new_shopping_list_formset()

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
    shopping_list.delete()
    return render_to_response('index.html', locals(), RequestContext(request))


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
            shopping_list.description = shopping_list_form.cleaned_data["description"]
            shopping_list.name = shopping_list_form.cleaned_data["name"]
            for items in shopping_list.items.all():
                items.delete()
            shopping_list.save()

            for f in ingredient_formset:
                ingredient = Ingredient(unit=f.cleaned_data['unit'], name=f.cleaned_data['name'],
                                        value=f.cleaned_data['value'])
                ingredient.save()
                shopping_list.items.add(ingredient)
                shopping_list.save()
            return render_to_response('index.html', locals(), RequestContext(request))
    else:
        recipe_form = AddNewProductList()
        ingredient_formset = new_shopping_list_formset()
    recipe_form = AddNewShoppingList(
        initial={'name': shopping_list.name, 'description': shopping_list.description})
    ingredient_formset = formset_factory(AddIngredient, extra=0, max_num=10, formset=RequiredFormSet)
    ingredients_list = shopping_list.items.all()
    formset = ingredient_formset(
        initial=[{'name': item.name, 'value': item.value, 'unit': item.unit} for item in ingredients_list])

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
            return render_to_response('index.html', locals(), RequestContext(request))
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
    product_list.delete()
    return render_to_response('index.html', locals(), RequestContext(request))


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
            return render_to_response('index.html', locals(), RequestContext(request))
    else:
        recipe_form = AddNewProductList()
        ingredient_formset = new_product_list_formset()
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
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


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


def test(request):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        id = event['id']
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
    return HttpResponse(events)


def add_event(request):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    print("Adding to calendar")
    event = {
        'summary': 'Google I/O 2015',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': '2015-05-28T09:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2015-05-28T17:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=2'
        ],
        'attendees': [
            {'email': 'lpage@example.com'},
            {'email': 'sbrin@example.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    return HttpResponse('Event created: %s' % (event.get('htmlLink')))


def delete_event(event_id):
    #event_id = '_6co34dpk64rj6'
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return HttpResponse('Event removed')
