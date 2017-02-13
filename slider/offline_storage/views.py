from django.shortcuts import render
from django.http import HttpResponse,HttpRequest,HttpResponseRedirect
from django.conf import settings
from django.utils import timezone

import os
from offline_storage.models import *
from offline_storage.forms import *
from offline_storage import imgur,download

# Create your views here.
def index(request):
	context = {}
	return render(request,os.path.join("offline_storage","index.html"),context)

def album_list(request):
	if request.method == "POST":
		form = AlbumUrlForm(request.POST)
		if form.is_valid():
			album_url = form.cleaned_data["album_url"]
			#http:,'',imgur.com,'a','album_id'
			album_id = album_url.split('/')[4]
			print (album_id)
			return HttpResponseRedirect("/offline/album/"+album_id)
	else:
		album_list = Album.objects.all()
		form = AlbumUrlForm()
		context = {
			"album_list": album_list,
			"form": form,
		}
		return render(request,os.path.join("offline_storage","album_list.html"),context)

def album(request,album_id):
	try:
		a = Album.objects.get(album_id=album_id)
	except Album.DoesNotExist:
		add_album(album_id)
	return view_album(request,album_id)

def view_album(request,album_id):
	try:
		album = Album.objects.get(album_id=album_id)
		post_list = Post.objects.filter(album__album_id=album_id).order_by('id')
		post_id_list = list((post.post_id for post in post_list))
		context = {
			"album_data": album,
			"album_posts": post_list,
			"album_post_ids": post_id_list,
		}
	except Album.DoesNotExist as e:
		return HttpResponse(e)
	except Exception as e:
		print ("view_album: ", e)
		return HttpResponse(e)
	else:
		return render(request,"offline_storage/view_album.html",context)

def add_album(album_id):
	album = imgur.extract(album_id)
	a = Album.objects.create(album_id=album_id,title=album["title"],source=album["source"],download_date=timezone.now(),)

	img_list = []
	for post in album["posts"]:
		a.post_set.create(post_id=post["id"],image_url=post["url"],image_path=post["path"],text=post["text"],)
		img_list.append(("http:"+post["url"], os.path.join(settings.BASE_DIR,"offline_storage","static",post["path"])))
	download.store_list(img_list)
	return
