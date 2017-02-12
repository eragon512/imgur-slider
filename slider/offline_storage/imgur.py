import re,os,sys
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
	find_queue = []

	for pos,post in enumerate(postList):
		new_post_url = img_url(post)
		if new_post_url == "":
			find_queue.append((pos,post["id"]))
		album_data["posts"].append({
			"id": post["id"],
			"text": offline_convert(post.find_all("div","post-image-meta")[0].prettify()),
			"url": new_post_url,
			"path": "offline_storage/images/"+album_data["id"]+"/"+os.path.basename(new_post_url),
		})
		sys.stdout.write("extract: "+new_post_url+"\n")

	for pos,post_id in find_queue:
		new_post_url = getImgUrl(post_id)
		album_data["posts"][pos]["url"] = new_post_url
		album_data["posts"][pos]["path"] = "offline_storage/images/"+album_data["id"]+"/"+os.path.basename(new_post_url)
	sys.stdout.write("\n\n")
	sys.stdout.write(repr(album_data))
	sys.stdout.write("\n\n")
	return album_data

def getImgUrl(post_id):
	req_text = requests.get("http://imgur.com/"+post_id).text
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

def offline_convert(text):
	return text.replace("http://imgur.com/a/", "/offline/album/")
