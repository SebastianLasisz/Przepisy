from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib.auth import logout, authenticate, login
from django.template.context_processors import csrf

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
            except:
                error = "That user name is already taken"
                return render_to_response('register.html', locals(), RequestContext(request))
        else:
            return render_to_response('register.html', locals(), RequestContext(request))
        return render_to_response('index.html', locals(), RequestContext(request))
    else:
        form = AddNewMeal()

    return render(request, 'create.html', {
        'form': form,
        'name': 'Create Meal'
    })


def create_recipe(request):
    if request.method == 'POST':
        form = AddNewRecipe(request.POST)
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
            except:
                error = "That user name is already taken"
                return render_to_response('register.html', locals(), RequestContext(request))
        else:
            return render_to_response('register.html', locals(), RequestContext(request))
        return render_to_response('index.html', locals(), RequestContext(request))
    else:
        form = AddNewRecipe()

    return render(request, 'create.html', {
        'form': form,
        'name': 'Create recipe'
    })


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


from django.forms.formsets import formset_factory
from django.shortcuts import render


def test_profile_settings(request):
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    newRecipeFormSet = formset_factory(AddIngredient, max_num=10, formset=RequiredFormSet)
    if request.method == 'POST':
        recipe_form = AddNewRecipe(request.POST)
        ingredient_formset = newRecipeFormSet(request.POST, request.FILES)

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
        ingredient_formset = newRecipeFormSet()

    c = {'recipe_form': recipe_form,
         'ingredient_formset': ingredient_formset,
         }
    c.update(csrf(request))
    return render_to_response('todo/index.html', c)
