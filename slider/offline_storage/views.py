from django.shortcuts import render
from django.http import HttpResponse,HttpRequest,HttpResponseRedirect
from django.conf import settings
from django.utils import timezone
from offline_storage.models import *
from offline_storage.forms import *
import re,os,sys
import queue, multiprocessing, threading
from bs4 import BeautifulSoup
import requests
import ntpath, urllib.request
from PIL import Image

# Create your views here.
def index(request):
	context = {}
	return render(request,"offline_storage/index.html",context)

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
		return render(request,"offline_storage/album_list.html",context)

def album(request,album_id):
	try:
		a = Album.objects.get(album_id=album_id)
	except Album.DoesNotExist:
		add_album(album_id)
	return view_album(request,album_id)


def add_album(album_id):
	album = extract(album_id)
	a = Album.objects.create(album_id=album_id,title=album["title"],source=album["source"],download_date=timezone.now(),)
	print (a)

	argument_list = []
	for post in album["posts"]:
		a.post_set.create(post_id=post["id"],image_url=post["url"],image_path=post["path"],text=post["text"],)
		argument_list.append(("http:"+post["url"], settings.BASE_DIR+"/offline_storage/static/"+post["path"],))

	pool = multiprocessing.Pool(processes=8)
	pool.starmap(download,argument_list)
	pool.close()
	pool.join()
	return

def view_album(request,album_id):
	try:
		album = Album.objects.get(album_id=album_id)
		post_list = Post.objects.filter(album__album_id=album_id).order_by('id')
		post_id_list = list((post.post_id for post in post_list))
		for post in post_list:
			if not os.path.exists(settings.BASE_DIR+"/offline_storage/static/"+post.image_path):
				print ("view_al",post.image_url)
				p = multiprocessing.Process(target=download,args=("http:"+post.image_url,settings.BASE_DIR+"/offline_storage/static/"+post.image_path,))
				p.start()
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

def download(img_url,img_path):
	if os.path.exists(img_path):
		print("File alrady downloaded: ",img_path)
		return

	tmp = urllib.request.urlopen(img_url)
	#print ("download: ",img_path)
	if not os.path.exists(os.path.dirname(img_path)):
		os.makedirs(os.path.dirname(img_path))
	f = open(img_path,"wb")
	for line in tmp:
		f.write(line)
	f.close()

	if os.path.exists(img_path):
		print ("finished:",img_url)
	else:
		print ("not finished:",img_url)
	return

def extract(album_id):
	def getImgUrl(post_id):
		tmp_soup = BeautifulSoup(requests.get("http://imgur.com/"+post_id).text,"html5lib")
		try:
			new_post_url = tmp_soup.find("img",itemprop="contentURL")["src"]
		except TypeError:
			new_post_url = str(re.findall("gifUrl: (.*)'(.*)',", tmp_soup.find("div",class_="post-image").div.script.string)[0][1])
		return new_post_url

	album_req = requests.get("http://imgur.com/a/"+album_id)
	a_data = album_req.text
	albumDataSoup = BeautifulSoup(a_data,"html5lib")
	album_data = {
		"id" : album_id,
		"posts" : [],
		"title": albumDataSoup.find("h1",class_="post-title").string
	}
	try:
		album_data["source"] = str(albumDataSoup.find("div",class_="post-title-meta").a["href"])
	except TypeError:
		#album_data["title"] = albumDataSoup.find("h1",class_="post-title").string
		album_data["source"] = "Unknown"

	req = requests.get("http://imgur.com/a/"+album_id+"/all")
	data = req.text
	dataSoup = BeautifulSoup(data,"html5lib")
	#print album_data
	postList = dataSoup.find_all("div","post-image-container")
	find_queue = queue.Queue()

	for pos,post in enumerate(postList):
		try:
			new_post_url = post.find("img",itemprop="contentURL")["src"]
		# if not an image file, check for gif
		except TypeError as e:
			try:
				new_post_url = str(re.findall("gifUrl: (.*)'(.*)',", post.find("script").string)[0][1])
			#if not a gif file, check for video
			except AttributeError:
				try:
					new_post_url = post.find("source")["src"]
				# if none of the above, might be an error
				except TypeError as e:
					sys.stdout.write(repr(e)+"\n")
					find_queue.put((pos,post["id"]))
					new_post_url = ""

		album_data["posts"].append({
			"id": post["id"],
			"text": offline_url(post.find_all("div","post-image-meta")[0].prettify()),
			"url": new_post_url,
			"path": "offline_storage/images/"+album_data["id"]+"/"+os.path.basename(new_post_url),
		})
		sys.stdout.write("extract: "+new_post_url+"\n")


	q = queue.Queue()
	threadLock = threading.Lock()
	def worker(pos,post_id):
		new_post_url = getImgUrl(post_id)
		threadLock.acquire()
		album_data["posts"][pos]["url"] = new_post_url
		album_data["posts"][pos]["path"] = "offline_storage/images/"+album_data["id"]+"/"+os.path.basename(new_post_url)
		threadLock.release()

	while not find_queue.empty():
		try:
			pos,post_id = find_queue.get()
			new_thread = threading.Thread(target=worker,args=(pos,post_id))
			new_thread.start()
			new_thread.join()
			sys.stdout.write("extract-redo: "+album_data["posts"][pos]["url"]+"\n")
		except Exception as e:
			print (type(e),e)
			find_queue.put((pos,post_id))

	print("\n\n",album_data,"\n\n")
	return album_data

def offline_url(text):
	return text.replace("http://imgur.com/a/", "/offline/album/")
