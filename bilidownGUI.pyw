import base64
import tkinter
import tkinter.messagebox
import sys
import json

# bilidown GUI


def get_param():
    argv = sys.argv
    argc = len(argv)
    if(argc < 2):
        return None
    else:
        return argv[1]

# base64 to json


def parseParam(str):
    if not str.startswith("bilidown://"):
        return None
    str = str.replace("bilidown://", "")
    try:
        decoded = base64.b64decode(str).decode()
        param_json = json.loads(decoded)
        return param_json
    except:
        return None


def main():
    root = tkinter.Tk()
    root.withdraw()
    param = get_param()
    if(param == None):
        tkinter.messagebox.showerror("bilidownGUI", "请传入下载参数", parent=root)
    else:
        param_json = parseParam(param)
        tkinter.messagebox.showinfo("bilidownGUI", "V:%s\r\n\r\nA:%s\r\n\r\nP:%s" % (
            param_json['v'], param_json['a'], param_json['p']), parent=root)
        # TODO display GUI


if __name__ == '__main__':
    main()
