import base64
import math
import os
import sys
import json
import re
import time
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
    match_obj = re.search(r'\d+', filename)
    if match_obj != None:
        return match_obj.group()
    else:
        return -1


def isPySuffix():
    return os.path.exists(os.path.join(os.path.dirname(__file__), "PY_SUFFIX"))


class BilidownGUI(QObject):
    sigExit = pyqtSignal()
    sigMin = pyqtSignal()
    sigUI = pyqtSignal(QVariant)

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
        self.procgress = 0

    def notifyUI(self, json):
        self.sigUI.emit(QVariant(json))

    def notifyProgress(self, perc, enforce=False):
        # decrease message cost
        if (self.procgress != perc) or enforce:
            self.procgress = perc
            self.notifyUI({
                "type": 'progress',
                "data": perc
            })

    def notifyInfo(self, type, info):
        styleMap = {
            0: 'info',
            1: 'danger',
            2: 'warning',
            3: 'success'
        }
        style = 'alert alert-%s' % (styleMap.get(type, 'default'))
        self.notifyUI({
            "type": 'info',
            "data": {
                "type": type,
                "style": style,
                "info": info
            }
        })

    def getPercentage(a, b):
        perc = float(a)/b
        return math.floor(perc*100)

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
            self.notifyProgress(BilidownGUI.getPercentage(
                self.lenAudioCurrent, self.lenAudio))
        elif result == True:
            self.audioThreadCount += 1
            if self.audioThreadCount == self.fdownInst.thread_count():
                self.fAudio.close()
                self.notifyInfo(0, "正在下载视频文件...")
                self.notifyProgress(0, True)
                time.sleep(0.2)
                self.fdownInst.download(
                    self.param_json['v'], self.headers, self.fVideo, 20, self.lenVideo, False, self.videoRecvCallback)
        else:
            self.fdownInst.terminate()
            self.releaseFileHandler()
            self.notifyInfo(1, "音频文件下载失败")

    def videoRecvCallback(self, jsonData):
        result = jsonData.get('result', None)
        if result == None:
            len = jsonData['len']
            self.lenVideoCurrent += len
            self.notifyProgress(BilidownGUI.getPercentage(
                self.lenVideoCurrent, self.lenVideo))
        elif result == True:
            self.videoThreadCount += 1
            if self.videoThreadCount == self.fdownInst.thread_count():
                self.fVideo.close()
                self.notifyInfo(0, "文件下载完成,正在合成完整视频...")
                self.notifyProgress(0, True)
                time.sleep(0.2)
                self.videoRemux()
        else:
            self.fdownInst.terminate()
            self.releaseFileHandler()
            self.notifyInfo(1, "视频文件下载失败")

    def videoRemux(self):
        avcom = AVCombine()
        avcom.setAudio(BilidownGUI.getAbsolutePath(
            self.downDirectory, self.filenameAudio))
        avcom.setVideo(BilidownGUI.getAbsolutePath(
            self.downDirectory, self.filenameVideo))
        avcom.setOutPath(BilidownGUI.getAbsolutePath(
            self.downDirectory, self.filenameOutput))
        # event
        avcom.setCallbackAudio(self.audioFrameCallback)
        avcom.setCallbackVideo(self.videoFrameCallback)
        if avcom.OpenStream():
            # frames
            self._audioFrame = avcom.getAudioFrame()
            self._videoFrame = avcom.getVideoFrame()
            if avcom.WriteToFile():
                avcom.releaseInstance()
                self.deleteTempM4s()
                self.notifyInfo(3, "视频合成成功")
            else:
                self.notifyInfo(1, "视频文件写入失败,无法写入文件。")
        else:
            self.notifyInfo(1, "视频文件合成失败,无法打开文件流。")

    def videoFrameCallback(self, x):
        self.notifyProgress(BilidownGUI.getPercentage(
            x+self._audioFrame, self._videoFrame+self._audioFrame))
        if(x == self._videoFrame):
            pass

    def audioFrameCallback(self, x):
        self.notifyProgress(BilidownGUI.getPercentage(
            x, self._videoFrame+self._audioFrame))
        if(x == self._audioFrame):
            self.notifyInfo(0, "视频拷贝完成，正在拷贝音频")
            time.sleep(0.2)

    def removeFile(self, path):
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

    def deleteTempM4s(self):
        self.removeFile(BilidownGUI.getAbsolutePath(
            self.downDirectory, self.filenameAudio))
        self.removeFile(BilidownGUI.getAbsolutePath(
            self.downDirectory, self.filenameVideo))

    @pyqtSlot()
    def onStartDownload(self):
        self.fdownInst.download(
            self.param_json['a'], self.headers, self.fAudio, 20, self.lenAudio, False, self.audioRecvCallback)

    def executeDownload(self):
        self.notifyInfo(0, "正在下载音频文件...")
        self.notifyProgress(0, True)
        QTimer.singleShot(200, self.onStartDownload)

    def getAbsolutePath(root, filename):
        return os.path.join(root, filename)

    @pyqtSlot()
    def onQuitClick(self):
        if self.fdownInst != None:
            self.fdownInst.terminate()
        self.sigExit.emit()

    @pyqtSlot()
    def onMinimizeClick(self):
        self.sigMin.emit()

    @pyqtSlot(result=str)
    def onGetParam(self):
        return self.param

    def getRootDirectory():
        if isPySuffix():
            return os.path.dirname(__file__)
        else:
            return os.path.dirname(sys.executable)

    @pyqtSlot(result=str)
    def onGetRootDirectory(self):
        return BilidownGUI.getRootDirectory()

    @pyqtSlot(result=str)
    def onBrowseDirectoryClick(self):
        directory = QFileDialog.getExistingDirectory(
            self._parent, "选择视频存放路径", BilidownGUI.getRootDirectory())
        return directory

    @pyqtSlot(str, str)
    def onDownloadClick(self, url, directory):
        self.downDirectory = directory
        self.param_json = parse_param(url)
        if self.param_json == None:
            self.notifyInfo(1, "URL格式错误无法解析")
            return
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

        self.fAudio = open(BilidownGUI.getAbsolutePath(
            self.downDirectory, self.filenameAudio), "wb")
        self.fVideo = open(BilidownGUI.getAbsolutePath(
            self.downDirectory, self.filenameVideo), "wb")
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
    view.setWindowIcon(QIcon(os.path.realpath(
        os.path.dirname(__file__) + "/assets/image/favicon.png")))
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
        __file__) + "/assets/bilidownGUI.html")
    view.page().load(QUrl.fromLocalFile(page_path))
    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
