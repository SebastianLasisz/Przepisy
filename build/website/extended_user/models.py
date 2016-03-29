from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='pic_folder/', default='pic_folder/None/no-img.jpg')
    signature = models.CharField(max_length=200)
    style = models.CharField(max_length=200, default='default')

    def __unicode__(self):
        return self.user.username
