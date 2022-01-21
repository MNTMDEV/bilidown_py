import threading
import requests
down_mutex = threading.Lock()

FDOWN_MAX_TRIAL = 5


def thread_output(tid, content):
    print("Thread[%d] %s" % (tid, content))


def down_thread(tid, url, headers, f, start, end):
    thread_output(
        tid, "[Info] Worker thread started,range %d-%d Byte." % (start, end))
    pos = start
    trial = 0
    while trial < FDOWN_MAX_TRIAL and pos <= end:
        headers['Range'] = 'bytes='+str(pos)+"-"+str(end)
        try:
            req = requests.get(url, headers=headers, stream=True)
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    # reset trial variable
                    trial = 0
                    # write file
                    down_mutex.acquire()
                    f.seek(pos)
                    f.write(chunk)
                    down_mutex.release()
                    pos += len(chunk)
            break
        except:
            trial += 1
            thread_output(
                tid, "[Info] Network error.Retring %d time(s)" % (trial))
    if(pos <= end):
        thread_output(
            tid, "[Warning] Max trial limit exceed.A part of bytes unable to download.")
    thread_output(tid, "[Info] Thread terminated.")


def down_len(url, headers):
    rhead = requests.head(url, headers=headers).headers
    len = int(rhead['Content-Length'])
    return len


def fdown(url, headers, f, n_thread, len):
    per_th = int(len/n_thread)
    if(len % n_thread > 0):
        n_thread += 1
    threads = []
    for i in range(n_thread):
        start = per_th * i
        end = per_th * (i+1)
        if(end > len):
            end = len
        end -= 1
        th = threading.Thread(target=down_thread, args=(i,
                                                        url, headers.copy(), f, start, end))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
