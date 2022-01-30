from fastdown import FDown

NUM_THREADS = 20


def get_m4s_filename(url):
    pos = url.find("?")
    if pos != -1:
        url = url[:pos]
    pos = url.rfind("/")
    if pos != -1:
        url = url[pos+1:]
    return url


if __name__ == '__main__':
    url = input("URL:")
    ref = input("Referer:")
    headers = {
        "Referer": ref,
        "Sec-Fetch-Mode": "no-cors",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }
    len = FDown.down_len(url, headers)
    print("File length is %d Bytes" % (len))
    filename = get_m4s_filename(url)
    f = open(filename, "wb")
    instance = FDown()
    instance.download(url, headers, f, NUM_THREADS, len, True, None)
    f.close()
    print("Complete!")
