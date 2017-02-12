import os, multiprocessing
import urllib

def store_list(file_list):
    pool = multiprocessing.Pool(processes=8)
    pool.starmap(download,file_list)
    pool.close()
    pool.join()

def store(url,path):
	if os.path.exists(img_path):
		print("File alrady downloaded: ",img_path)
		return
    tmp = urllib.request.urlopen(url)
    #print ("download: ",img_path)
    if not os.path.exists(os.path.dirname(path)):
		os.makedirs(os.path.dirname(path))
	f = open(path,"wb")
	for line in tmp:
		f.write(line)
	f.close()

    if size_match(url_request,path):
        sys.stdout.write("finished: "+path+"\n")
    else:
        sys.stdout.write("not-finished: "+path+"\n")
    return

def size_match(url_request,path):
    return (int(url_request.info()["Content-Length"]) == os.path.getsize(path))
