import threading
import requests

FDOWN_MAX_TRIAL = 5
DOWN_CHUNK_SIZE = 1024*1024
VIDEO_PART_UNIT = 8*DOWN_CHUNK_SIZE


class FDown:
    down_mutex = threading.Lock()
    threads = []
    callback = None
    _terminate = False
    callback_condition = threading.Condition()
    handler_ready = threading.Condition(threading.Lock())
    invoker_lock = threading.Lock()
    callback_param = None

    def thread_output(self, tid, content):
        print("Thread[%d] %s" % (tid, content))

    def invoke_callback(self, param):
        self.invoker_lock.acquire()

        self.callback_condition.acquire()
        self.callback_param = param
        self.callback_condition.notify()
        self.callback_condition.wait()
        self.callback_condition.release()

        self.invoker_lock.release()

    def down_thread(self, tid, url, headers, f, start, end):
        # self.thread_output(
        #     tid, "[Info] Worker thread started,range %d-%d Byte." % (start, end))
        pos = start
        trial = 0
        while trial < FDOWN_MAX_TRIAL and pos <= end:
            cur_end = pos+VIDEO_PART_UNIT-1
            if(cur_end > end):
                cur_end = end
            headers['Range'] = 'bytes='+str(pos)+"-"+str(cur_end)
            try:
                if self._terminate:
                    break
                req = requests.get(url, headers=headers,
                                   stream=True, timeout=5)
                total_fetch = 0
                cur_pos = pos
                for chunk in req.iter_content(chunk_size=DOWN_CHUNK_SIZE):
                    if self._terminate:
                        break
                    if chunk:
                        # reset trial variable
                        trial = 0
                        # write file
                        self.down_mutex.acquire()
                        f.seek(cur_pos)
                        f.write(chunk)
                        self.down_mutex.release()
                        cur_pos += len(chunk)
                        total_fetch += len(chunk)
                pos = cur_pos
                if self.callback != None:
                    self.invoke_callback({
                        "tid": tid,
                        "len": total_fetch
                    })
            except:
                trial += 1
                self.thread_output(
                    tid, "[Info] Network error.Retring %d time(s)" % (trial))
        if(pos <= end):
            self.thread_output(
                tid, "[Warning] Max trial limit exceed.A part of bytes unable to download.")
        # self.thread_output(tid, "[Info] Thread terminated.")
        if self.callback != None:
            self.invoke_callback({
                "tid": tid,
                "result": pos > end
            })
        return pos > end

    def down_len(url, headers):
        try:
            rhead = requests.head(url, headers=headers).headers
            len = int(rhead['Content-Length'])
            return len
        except:
            return -1

    def handler(self, url, headers, f, n_thread, len, sync, callback):
        self._terminate = False
        self.callback = callback
        self.threads = []
        per_th = int(len/n_thread)
        rest = len % n_thread
        for i in range(n_thread):
            start = per_th * i + min(i, rest)
            end = per_th * (i+1) + min(i+1, rest)
            if(end > len):
                end = len
            end -= 1
            th = threading.Thread(target=self.down_thread, args=(i,
                                                                 url, headers.copy(), f, start, end))
            self.threads.append(th)

        finished = 0
        if self.callback != None:
            self.callback_condition.acquire()
            for th in self.threads:
                th.start()
            while finished < n_thread:
                self.callback_condition.wait()
                self.callback_condition.notify()
                param = self.callback_param
                result = param.get('result', None)
                if result != None:
                    finished += 1
                if finished == n_thread:
                    self.callback_condition.release()
                self.callback(param)
            if n_thread == 0:
                self.callback_condition.release()
        for th in self.threads:
            th.join()

    def download(self, url, headers, f, n_thread, len, sync, callback):
        handler_thread = threading.Thread(target=self.handler, args=(
            url, headers, f, n_thread, len, sync, callback))
        handler_thread.start()
        if sync:
            handler_thread.join()
            return True
        else:
            return True

    def thread_count(self):
        return len(self.threads)

    def suspend(self):
        self.down_mutex.acquire()

    def resume(self):
        self.down_mutex.release()

    def terminate(self, sync=False):
        self._terminate = True
        if sync:
            for th in self.threads:
                if th is not threading.current_thread():
                    th.join()
