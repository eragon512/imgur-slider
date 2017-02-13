import re, os, sys
from bs4 import BeautifulSoup
import requests

def extract(album_id):
	album_req = requests.get("http://imgur.com/a/"+album_id)
	a_data = album_req.text
	albumDataSoup = BeautifulSoup(a_data,"html5lib")
	album_data = {
		"id" : album_id,
		"posts" : [],
		"title": ""+str(albumDataSoup.find("h1",class_="post-title").string)
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
	find_list = []

	for pos,post in enumerate(postList):
		new_post_url = img_url(post)
		if new_post_url == "":
			find_list.append((pos,post["id"]))
		album_data["posts"].append({
			"id": post["id"],
			"text": purify_imgtext(str(post.find("div","post-image-meta"))),
			"url": new_post_url,
			"path": os.path.join("offline_storage","images",album_data["id"],os.path.basename(new_post_url)),
		})
		sys.stdout.write("extract: "+new_post_url+"\n")

	url_list = getImgUrlList(find_list)
	for pos,url in url_list:
		album_data["posts"][pos]["url"] = url
		album_data["posts"][pos]["path"] = os.path.join("offline_storage","images",album_data["id"],os.path.basename(url))

	sys.stdout.write("\n\n-----------image url extraction finished ----------------\n\n")
	return album_data

import multiprocessing
def getImgUrlList(post_list):
	pool = multiprocessing.Pool(processes=8)
	url_list = pool.starmap(getImgUrlListWorker,post_list)
	pool.close()
	pool.join()
	return url_list

def getImgUrlListWorker(pos,post_id):
	return (pos,getImgUrl(post_id))

def getImgUrl(post_id):
	req_text = requests.get("http://imgur.com/"+post_id).text
	tmp_soup = BeautifulSoup(req_text,"html5lib")
	sys.stdout.write("redo-extract: http://imgur.com/"+post_id+"\n")
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

def purify_imgtext(text):
	return offline_convert(text.replace(". ", ".<br/>"))

def offline_convert(text):
	text = text.replace("https://imgur.com/a/", "/offline/album/")
	text = text.replace("http://imgur.com/a/", "/offline/album/")
	return text
