from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib.auth import logout, authenticate, login
from extended_user.form import *
from extended_user.models import *
from recipe.form import *
from django.contrib.auth.hashers import make_password


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


def test(request):
    if request.user.is_authenticated():
        return HttpResponse("You are logged in.")
    else:
        return HttpResponse("You are not logged in.")
