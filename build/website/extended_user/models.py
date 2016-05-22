from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    use_google = models.BooleanField()
    use_trello = models.BooleanField()
    trello_key = models.CharField(max_length=64, blank=True)
    trello_board_name = models.CharField(max_length=100, default='Reshp', blank=True)

    def __unicode__(self):
        return self.user.username
