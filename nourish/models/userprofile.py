from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('E', 'Event Coordinator'),
        ('T', 'Theme Camp Organizer'),
        ('A', 'Art Project Organizer'),
    )
    url = models.URLField()
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)
    user = models.ForeignKey(User, unique=True)
    def __unicode__(self):
        return self.user.username
