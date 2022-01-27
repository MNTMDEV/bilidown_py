import base64
import os
import sys
import json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebChannel import *
from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *

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
    if not str.startswith("bilidown://"):
        return None
    str = str.replace("bilidown://", "")
    try:
        decoded = base64.b64decode(str).decode()
        param_json = json.loads(decoded)
        return param_json
    except:
        return None


class BilidownGUI(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    @property
    def param_json(self):
        return self._param_json

    @param_json.setter
    def param_json(self, value):
        self._param_json = value

    @pyqtSlot()
    def onDownloadClick(self):
        pass


def main():
    # get parameters
    param = get_param()
    param_json = None
    if param != None:
        param_json = parse_param(param)
    # Qt initialization
    app = QApplication(sys.argv)

    view = QWebEngineView()
    # Window transparency settings
    view.setWindowFlags(Qt.FramelessWindowHint)
    view.setAttribute(Qt.WA_TranslucentBackground)
    view.page().setBackgroundColor(Qt.transparent)
    channel = QWebChannel()
    obj = BilidownGUI()
    obj.param_json = param_json
    channel.registerObject("BilidownGUI", obj)
    view.page().setWebChannel(channel)
    page_path = os.path.realpath(os.path.dirname(
        __file__)+"/assets/bilidownGUI.html")
    view.page().load(QUrl.fromLocalFile(page_path))
    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
