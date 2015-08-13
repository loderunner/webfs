from threading import Timer
from time import time

OPEN_FILE_TIMEOUT = 20.0

files = {}

def open_file(path):
    f = files.get(path)
    if f is None:
        f = {'file' : open(path, 'rb'), 'time' : time()}
        files[path] = f
    else:
        f['time'] = time()
    return f['file']

def clear_cache():
    to_close = []
    for path in files:
        f = files[path]
        if (time() - f['time']) > OPEN_FILE_TIMEOUT:
            f['file'].close()
            to_close.append(path)
    for path in to_close:
        files.pop(path)
    timer = Timer(10.0, clear_cache)
    timer.daemon = True
    timer.start()

clear_cache()