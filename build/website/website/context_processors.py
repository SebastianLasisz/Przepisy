from django.contrib.auth.models import User
from extended_user.models import UserProfile


def style(request):
    try:
        if request.user.is_authenticated():
            user = UserProfile.objects.get(user=User.objects.get(username=request.user.username))
            return {'style': user.style}
        else:
            return {}
    except:
        return {}
