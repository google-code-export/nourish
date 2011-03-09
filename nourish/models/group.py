from django.db import models
from django.contrib.auth.models import User

class GroupManager(models.Manager):
	def add_admin(self, group, admin):
		GroupUser.objects.create(group=group, user=admin, admin=True)

class Group(models.Model):
	name = models.CharField(max_length=100, unique=True)
	objects = GroupManager()
	def __unicode__(self):
		return self.name
	def get_absolute_url(self):
		return '/groups/%i/' % self.id

class GroupUser(models.Model):
	group = models.ForeignKey(Group)
	user = models.ForeignKey(User)
	admin = models.BooleanField()
	def __unicode__(self):
		return self.group.name + ' : ' + self.user.username
