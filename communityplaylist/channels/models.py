from django.db import models
from django.contrib.auth.models import User

class Channel(models.Model):
	creator = models.ForeignKey(User)
	created_at = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		value = "Created at %s by %s" %(self.created_at,self.creator)
		return value

# Create your models here.
class Playlist(models.Model):
	channel = models.ForeignKey(Channel)
	url = models.CharField(max_length=20)
	played = models.BooleanField(default=False)
	removed = models.BooleanField(default=False)

	class Meta:
		unique_together = ("url", "played","removed")

	def __unicode__(self):
		return self.url
		
class Vote(models.Model):
	video = models.ForeignKey(Playlist)
	# In the future tag column should be changed to some fk kind 
	tag = models.CharField(max_length=100)
	positive = models.IntegerField(default=0)
	negative = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		value = "%s voted (%d,%d) by %s at %s" %(self.video.url,self.positive,self.negative,self.tag,self.created_at)
		return value
