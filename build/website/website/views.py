from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import logout, authenticate, login


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


def test(request):
    if request.user.is_authenticated():
        return HttpResponse("You are logged in.")
    else:
        return HttpResponse("You are not logged in.")