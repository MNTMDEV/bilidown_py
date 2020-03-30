import requests
import threading
import fastdown

NUM_THREADS=20

url=input("URL:")
ref=input("Referer:")
headers={
"Referer": ref,
"Sec-Fetch-Mode":"no-cors",
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}
len=fastdown.down_len(url,headers)
f = open("1.tmp", "wb")
fastdown.fdown(url,headers,f,NUM_THREADS,len)
