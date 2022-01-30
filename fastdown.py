from gc import callbacks
import threading
from unittest import result
import requests

FDOWN_MAX_TRIAL = 5


class FDown:
    down_mutex = threading.Lock()
    threads = []
    callback = None
    _terminate = False

    def thread_output(self, tid, content):
        print("Thread[%d] %s" % (tid, content))

    def down_thread(self, tid, url, headers, f, start, end):
        # self.thread_output(
        #     tid, "[Info] Worker thread started,range %d-%d Byte." % (start, end))
        pos = start
        trial = 0
        while trial < FDOWN_MAX_TRIAL and pos <= end:
            headers['Range'] = 'bytes='+str(pos)+"-"+str(end)
            try:
                req = requests.get(url, headers=headers, stream=True)
                for chunk in req.iter_content(chunk_size=1024):
                    if self._terminate:
                        return pos > end
                    if chunk:
                        # reset trial variable
                        trial = 0
                        # write file
                        self.down_mutex.acquire()
                        f.seek(pos)
                        f.write(chunk)
                        self.down_mutex.release()
                        pos += len(chunk)
                        if self.callback != None:
                            self.callback({
                                "tid": tid,
                                "len": len(chunk)
                            })
                break
            except:
                trial += 1
                self.thread_output(
                    tid, "[Info] Network error.Retring %d time(s)" % (trial))
        if(pos <= end):
            self.thread_output(
                tid, "[Warning] Max trial limit exceed.A part of bytes unable to download.")
        # self.thread_output(tid, "[Info] Thread terminated.")
        if self.callback != None:
            if self.callback != None:
                self.callback({
                    "tid": tid,
                    "result": pos > end
                })
        return pos > end

    def down_len(url, headers):
        rhead = requests.head(url, headers=headers).headers
        len = int(rhead['Content-Length'])
        return len

    def download(self, url, headers, f, n_thread, len, sync, callback):
        self._terminate = False
        self.callback = callback
        self.threads = []
        per_th = int(len/n_thread)
        if(len % n_thread > 0):
            n_thread += 1
        for i in range(n_thread):
            start = per_th * i
            end = per_th * (i+1)
            if(end > len):
                end = len
            end -= 1
            th = threading.Thread(target=self.down_thread, args=(i,
                                                                 url, headers.copy(), f, start, end))
            th.start()
            self.threads.append(th)
        if sync:
            for th in self.threads:
                th.join()
            return True
        else:
            return True

    def thread_count(self):
        return len(self.threads)

    def suspend(self):
        self.down_mutex.acquire()

    def resume(self):
        self.down_mutex.release()

    def terminate(self):
        self._terminate = True
        for th in self.threads:
            if self is not threading.current_thread():
                th.join()
