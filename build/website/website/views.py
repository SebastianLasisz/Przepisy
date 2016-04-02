from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, render
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


class ShowAllMeals(ListView):
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
         'ingredient_formset': ingredient_formset,
         }
    c.update(csrf(request))
    return render_to_response('todo/index.html', c)


def delete_recipe(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    recipe = Recipe.objects.get(id=pk)
    recipe.delete()
    return render_to_response('index.html', locals(), RequestContext(request))


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
    number_of_extras = (recipe.ingredients.count() - 1)
    ingredient_formset = formset_factory(AddIngredient, max_num=10, formset=RequiredFormSet)
    ingredients_list = recipe.ingredients.all()
    formset = ingredient_formset(
        initial=[{'name': item.name, 'value': item.value, 'unit': item.unit} for item in ingredients_list])

    c = {'recipe_form': recipe_form,
         'ingredient_formset': formset,
         }
    c.update(csrf(request))
    return render_to_response('todo/index.html', c)


class ShowAllRecipes(ListView):
    context_object_name = 'recipe'
    queryset = Recipe.objects.filter(global_access=False)
    queryset2 = Recipe.objects.filter(global_access=True)

    def get_context_data(self, **kwargs):
        queryset = Recipe.objects.filter(user=self.request.user)
        queryset2 = Recipe.objects.filter(global_access=True)
        context = {
            'paginator': None,
            'page_obj': None,
            'is_paginated': False,
            'object_list': queryset,
            'object_list2': queryset2
        }
        context.update(kwargs)
        return context


def show_recipe(request, **kwargs):
    pk = int(kwargs.get('pk', None))
    try:
        recipe = Recipe.objects.get(id=pk)
        return render_to_response('recipe.html', locals(), RequestContext(request))
    except:
        return HttpResponse(status=404)


def edit_shopping_list(request):
    return


def edit_product_list(request):
    return
