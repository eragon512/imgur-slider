import re, os, sys, multiprocessing
from bs4 import BeautifulSoup
import requests
try:
	import urllib.parse as urlparse
# if python2
except ImportError:
	import urlparse
	import itertools

def extract(album_id):
	req = requests.get("http://imgur.com/a/"+album_id)
	data = req.text
	dataSoup = BeautifulSoup(data,"html5lib")
	album_data = {
		"id" : album_id,
		"posts" : [],
		"title": ""+str(dataSoup.find("h1").string)
	}
	try:
		album_data["source"] = str(dataSoup.find("div",class_="post-title-meta").a)
	except TypeError:
		#album_data["title"] = albumDataSoup.find("h1",class_="post-title").string
		album_data["source"] = "Unknown"

	#print album_data
	find_list = []
	postList = dataSoup.find_all("div","post-image-container")

	for pos,post in enumerate(postList):
		new_post_url = img_url(post)
		if new_post_url == "":
			find_list.append((pos,post["id"]))
		album_data["posts"].append({
			"id": post["id"],
			"text": purify_imgtext(str(post.find("div","post-image-meta"))),
			"url": new_post_url,
			"path": os.path.join("offline_storage","images",album_data["id"],url_filename(new_post_url)),
		})
		if new_post_url != "":
			sys.stdout.write("extract: "+new_post_url+"\n")

	url_list = getImgUrlList(find_list)
	for pos,url in url_list:
		album_data["posts"][pos]["url"] = url
		album_data["posts"][pos]["path"] = os.path.join("offline_storage","images",album_data["id"],url_filename(url))
		sys.stdout.write("redo-extract: "+url+"\n")

	sys.stdout.write("\n\n-----------image url extraction finished ----------------\n\n")
	return album_data

def getImgUrlList(post_list):
	try:
		pool = multiprocessing.Pool(processes=8)
		url_list = pool.starmap(getImgUrlListWorker,post_list)
		pool.close()
		pool.join()
	# if python2, then pool.starmap gives attribute
	except AttributeError:
		url_list = list(itertools.starmap(getImgUrlListWorker,post_list))
	finally:
		return url_list

def getImgUrlListWorker(pos,post_id):
	return (pos,getImgUrl(post_id))

def getImgUrl(post_id):
	url_path = "//i.imgur.com/"+post_id
	try:
		content_type = requests.head("http:"+url_path+".jpg").headers["Content-Type"]
	except requests.exceptions.ConnectionError:
		sys.stdout.write("exception: getImgUrl: "+ url_path +"\n")
	else:
		#sys.stdout.write(url_path +"\t"+ content_type +"\n")
		if content_type == "image/jpeg":
			return url_path + ".jpg"
		elif content_type == "image/png":
			return url_path + ".png"
		elif content_type == "image/gif":
			return url_path + ".gif"
		elif content_type == "video/mp4":
			return url_path + ".mp4"
		else:
			tmp_soup = BeautifulSoup(req_text,"html5lib")
			return img_url(tmp_soup)

def img_url(soup):
    url = ""
    try:
        url = soup.find("img",itemprop="contentURL")["src"]
    except AttributeError:
        url = post.find("source")["src"]
    except TypeError:
        url = str(re.findall("gifUrl: (.*)'(.*)',", soup.find("div",class_="post-image").div.script.string)[0][1])
    except AttributeError or TypeError:
        print ("imgurl\n",soup)
        raise Exception("imgurl: No Image found in Soup")
    else:
        return url
    finally:
        return url

def url_filename(url):
	# 2 - path
	path = urlparse.urlsplit(url).path.strip('/')
	filename = path.split('/')[-1]
	return filename

def purify_imgtext(text):
	text = text.replace(". ", ".<br/>")
	text = text.replace("? ", "?<br/>")
	text = text.replace("! ", "!<br/>")
	return offline_convert(text)

def offline_convert(text):
	if text == None:
		return ""
	text = text.replace("https://imgur.com/a/", "/offline/album/")
	text = text.replace("http://imgur.com/a/", "/offline/album/")
	return text
