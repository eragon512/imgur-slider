from django.db import models

# Create your models here.
class Album(models.Model):
	album_id = models.CharField(unique=True,max_length=200)
	title = models.CharField(max_length=200)
	source = models.CharField(max_length=200,default="")
	download_date = models.DateTimeField()
	auto = models.BooleanField(default=False)
	#post_date = models.DateTimeField()
	def __str__(self):
		return self.title

class Post(models.Model):
	album = models.ForeignKey(Album,on_delete=models.CASCADE)
	post_id = models.CharField(max_length=200)
	image_url = models.CharField(max_length=200)
	image_path = models.CharField(max_length=200)
	text = models.CharField(max_length=200)
	def __str__(self):
		return self.post_id
