import base64
import os
import sys
import json
import re
from typing import overload
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebChannel import *
from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from bilidownObj import BilidownObj

# bilidown GUI


def get_param():
    argv = sys.argv
    argc = len(argv)
    if(argc < 2):
        return None
    else:
        return argv[1]


class BilidownGUI(QWebEngineView):
    def __init__(self):
        QWebEngineView.__init__(self)
        self.initMousePos()
        self.resize(600, 500)
        # set icon png
        self.setWindowIcon(QIcon(os.path.realpath(
            os.path.dirname(__file__) + "/assets/image/favicon.png")))
        self.windowTransparency()
        self.initObj()
        self.initChannel()
        self.load()
        self.focusProxy().installEventFilter(self)

    def initMousePos(self):
        self._isTrack = False
        self._startPos = None

    # Window transparency settings
    def windowTransparency(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.page().setBackgroundColor(Qt.transparent)

    def initObj(self):
        param = get_param()
        self._obj = BilidownObj()
        self._obj.param = param
        # event signal bind
        self._obj.sigExit.connect(self.close)
        self._obj.sigMin.connect(self.showMinimized)

    def initChannel(self):
        self._channel = QWebChannel()
        self._channel.registerObject("BilidownGUI", self._obj)
        self.page().setWebChannel(self._channel)

    def load(self):
        page_path = os.path.realpath(os.path.dirname(
            __file__) + "/assets/bilidownGUI.html")
        self.page().load(QUrl.fromLocalFile(page_path))

    def eventFilter(self, source, event):
        if self.focusProxy() is source:
            type = event.type()
            if type == QEvent.MouseButtonPress:
                self.mousePressEvent(event)
            elif type == QEvent.MouseButtonRelease:
                self.mouseReleaseEvent(event)
            elif type == QEvent.MouseMove:
                self.mouseMoveEvent(event)
        return super().eventFilter(source, event)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._isTrack = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._isTrack = False
            self._startPos = None

    def mouseMoveEvent(self, e):
        if self._isTrack:
            deltaPos = e.pos() - self._startPos
            self.move(self.pos()+deltaPos)


def main():
    # Qt initialization
    app = QApplication(sys.argv)
    view = BilidownGUI()
    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
