from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    use_google = models.BooleanField()
    google_calendar_name = models.CharField(max_length=100, default='primary')
    use_trello = models.BooleanField()
    trello_key = models.CharField(max_length=64)
    trello_board_name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.user.username
