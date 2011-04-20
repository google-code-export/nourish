from django.db import models
from django.contrib.auth.models import User

class GroupManager(models.Manager):
    def add_admin(self, group, admin):
        GroupUser.objects.create(group=group, user=admin, admin=True)

class GroupUser(models.Model):
    group = models.ForeignKey('Group')
    user = models.ForeignKey(User)
    admin = models.BooleanField()
    def __unicode__(self):
        return self.group.name + ' : ' + self.user.username

class Group(models.Model):
    ROLE_CHOICES = (
        ('T', 'Theme Camp'),
        ('A', 'Artist Group'),
    )
    name = models.CharField(max_length=100, unique=True, verbose_name="Group Name")
    objects = GroupManager()
    url = models.URLField(blank=True, null=True, verbose_name="Group Website")
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)
    members = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return '/groups/%i/' % self.id
    
    def user(self, user):
        try:
            gu = GroupUser.objects.get(user=user, group=self)
        except GroupUser.DoesNotExist:
            gu = GroupUser.objects.create(user=user, group=self)
        return gu
