import base64
import os
import sys
import json
import re
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebChannel import *
from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from fastdown import FDown
from libavcombine import AVCombine

# bilidown GUI


def get_param():
    argv = sys.argv
    argc = len(argv)
    if(argc < 2):
        return None
    else:
        return argv[1]

# base64 to json


def parse_param(str):
    if not str.startswith("bilidown://total/"):
        return None
    str = str.replace("bilidown://total/", "")
    try:
        decoded = base64.b64decode(str).decode()
        param_json = json.loads(decoded)
        return param_json
    except:
        return None


def get_m4s_filename(url):
    pos = url.find("?")
    if pos != -1:
        url = url[:pos]
    pos = url.rfind("/")
    if pos != -1:
        url = url[pos+1:]
    return url

def get_video_number(filename):
    match_obj = re.search(r'\d+',filename)
    if match_obj!=None:
        return match_obj.group()
    else:
        return -1

class BilidownGUI(QObject):
    sigExit = pyqtSignal()
    sigMin = pyqtSignal()

    def __init__(self, parent=None):
        self.parent = parent
        QObject.__init__(self, parent)
        self.initVariables()

    def initVariables(self):
        self.fdownInst = None
        self.filenameAudio = ""
        self.filenameVideo = ""
        self.filenameOutput = ""
        self.fAudio = None
        self.fVideo = None
        self.lenAudio = 0
        self.lenVideo = 0
        self.lenAudioCurrent = 0
        self.lenVideoCurrent = 0
        self.audioThreadCount = 0
        self.videoThreadCount = 0
        self._audioFrame = 0
        self._videoFrame = 0

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def param(self):
        return self._param

    @param.setter
    def param(self, value):
        self._param = value

    def releaseFileHandler(self):
        if self.fAudio != None:
            self.fAudio.close()
        if self.fAudio != None:
            self.fVideo.close()

    def audioRecvCallback(self, jsonData):
        result = jsonData.get('result', None)
        if result == None:
            len = jsonData['len']
            self.lenAudioCurrent += len
            # TODO notify
        elif result == True:
            self.audioThreadCount += 1
            if self.audioThreadCount == self.fdownInst.thread_count():
                self.fAudio.close()
                # TODO notify success
                self.fdownInst.download(
                    self.param_json['v'], self.headers, self.fVideo, 20, self.lenVideo, False, self.videoRecvCallback)
        else:
            self.fdownInst.terminate()
            self.releaseFileHandler()
            # TODO notify failure

    def videoRecvCallback(self, jsonData):
        result = jsonData.get('result', None)
        if result == None:
            len = jsonData['len']
            self.lenVideoCurrent += len
            # TODO notify
        elif result == True:
            self.videoThreadCount += 1
            if self.videoThreadCount == self.fdownInst.thread_count():
                self.fVideo.close()
                # TODO notify success
                self.videoRemux()
        else:
            self.fdownInst.terminate()
            self.releaseFileHandler()
            # TODO notify failure

    def videoRemux(self):
        avcom = AVCombine()
        avcom.setAudio(self.filenameAudio)
        avcom.setVideo(self.filenameVideo)
        avcom.setOutPath(self.filenameOutput)
        # event
        avcom.setCallbackAudio(self.videoFrameCallback)
        avcom.setCallbackVideo(self.videoFrameCallback)
        # frames
        self._audioFrame = avcom.getAudioFrame()
        self._videoFrame = avcom.getVideoFrame()
        if avcom.OpenStream():
            if avcom.WriteToFile():
                # notify success
                pass
            else:
                #notify failure
                pass
        else:
            # notify failure
            pass

    def videoFrameCallback(self, x):
        # notify info
        if(x == self._videoFrame):
            #finish
            pass

    def audioFrameCallback(self, x):
        # notify info
        if(x == self._audioFrame):
            #finish
            pass

    def executeDownload(self):
        self.fdownInst.download(
            self.param_json['a'], self.headers, self.fAudio, 20, self.lenAudio, False, self.audioRecvCallback)

    @pyqtSlot()
    def onQuitClick(self):
        self.sigExit.emit()

    @pyqtSlot()
    def onMinimizeClick(self):
        self.sigMin.emit()

    @pyqtSlot(result=str)
    def onGetParam(self):
        return self.param

    @pyqtSlot(result=str)
    def onBrowseDirectoryClick(self):
        directory = QFileDialog.getExistingDirectory(self._parent, "选择视频存放路径")
        return directory

    @pyqtSlot(str, str)
    def onDownloadClick(self, url, directory):
        self.downDirectory = directory
        self.param_json = parse_param(url)
        if self.param_json == None:
            return{
                "success": False,
                "msg": "URL格式错误无法解析"
            }
        self.headers = {
            "Referer": self.param_json['p'],
            "Sec-Fetch-Mode": "no-cors",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
        }
        self.initVariables()
        # fastdown
        self.fdownInst = FDown()
        self.lenAudio = FDown.down_len(self.param_json['a'], self.headers)
        self.lenVideo = FDown.down_len(self.param_json['v'], self.headers)
        self.filenameAudio = get_m4s_filename(self.param_json['a'])
        self.filenameVideo = get_m4s_filename(self.param_json['v'])
        self.filenameOutput = "%s.mp4" % (get_video_number(self.filenameAudio))

        self.fAudio = open(self.filenameAudio, "wb")
        self.fVideo = open(self.filenameVideo, "wb")
        # execute download
        self.executeDownload()

    @pyqtSlot()
    def onSuspendDownloadClick(self):
        pass

    @pyqtSlot()
    def onResumeDownloadClick(self):
        pass


def main():
    # get parameters
    param = get_param()
    # Qt initialization
    app = QApplication(sys.argv)

    view = QWebEngineView()
    view.resize(600, 500)
    # set icon png
    view.setWindowIcon(QIcon("assets/image/favicon.png"))
    # Window transparency settings
    view.setWindowFlags(Qt.FramelessWindowHint)
    view.setAttribute(Qt.WA_TranslucentBackground)
    view.page().setBackgroundColor(Qt.transparent)
    channel = QWebChannel()
    obj = BilidownGUI()
    obj.param = param
    channel.registerObject("BilidownGUI", obj)
    view.page().setWebChannel(channel)
    # event signal bind
    obj.sigExit.connect(view.close)
    obj.sigMin.connect(view.showMinimized)
    page_path = os.path.realpath(os.path.dirname(
        __file__)+"/assets/bilidownGUI.html")
    view.page().load(QUrl.fromLocalFile(page_path))
    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
