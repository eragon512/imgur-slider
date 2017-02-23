import os, sys, multiprocessing, itertools, errno
import requests

def store_list(file_list):
    try:
        pool = multiprocessing.Pool(processes=8)
        pool.starmap(store,file_list)
        pool.close()
        pool.join()
    except AttributeError:
        list(itertools.starmap(store,file_list))
    finally:
        sys.stdout.write("--------image downloads finished----------\n")

def store(url, path):
	try:
		os.makedirs(os.path.dirname(path))
	except OSError as e:
		# if python2, then pool.starmap gives attribute
		if e.errno != errno.EEXIST:
			raise
	if os.path.exists(path):
		print("already downloaded: ",path)
		return
	try:
		store_routine(url,path)
	except Exception as e:
		sys.stdout.write("exception: store: "+url+" - "+repr(e)+"\n")
		store_routine(url,path)
	return

def store_routine(url,path):
    tmp = requests.get(url,stream=True)
    with open(path,"wb") as f:
        for chunk in tmp.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    if size_match(tmp,path):
        sys.stdout.write("finished: "+url+"\n")
    else:
        sys.stdout.write("not-finished: "+url+"\n")

def size_match(url_request,path):
    return (int(url_request.headers["Content-Length"]) == os.path.getsize(path))
