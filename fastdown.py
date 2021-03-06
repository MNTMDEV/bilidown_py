import threading
import requests
down_mutex=threading.Lock()

def down_thread(url,headers,f,start,end):
    pos=start
    if(start>=end):
        return
    headers['Range']='bytes='+str(start)+"-"+str(end)
    req=requests.get(url,headers=headers,stream=True)
    for chunk in req.iter_content(chunk_size=1024):
        if chunk:
            # write file
            down_mutex.acquire()
            f.seek(pos)
            f.write(chunk)
            down_mutex.release()
            pos+=len(chunk)

def down_len(url,headers):
    rhead=requests.head(url,headers=headers).headers
    len=int(rhead['Content-Length'])
    return len

def fdown(url,headers,f,n_thread,len):
    per_th=int(len/n_thread)
    if(len%n_thread>0):
        n_thread+=1
    # f = open("1.flv", "wb")
    threads=[]
    for i in range(n_thread):
        start=per_th*i
        end=per_th*(i+1)
        if(end>len):
            end=len
        end-=1
        th=threading.Thread(target=down_thread,args=(url,headers.copy(),f,start,end))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()