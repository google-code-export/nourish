from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
	name = models.CharField(max_length=100, unique=True)
	def __unicode__(self):
		return self.name

class GroupUser(models.Model):
	group = models.ForeignKey(Group)
	user = models.ForeignKey(User)
	admin = models.BooleanField()
	def __unicode__(self):
		return self.group.name + ' : ' + self.user.username

