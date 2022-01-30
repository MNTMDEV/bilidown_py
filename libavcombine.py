import ctypes
import os
from types import FunctionType


class AVCombine(object):
    dllInvoker = None
    _instance = None

    def initVar(self):
        self.linkDll()
        self.initFunction()
        self._instance = self._getInstance()
    
    def releaseInstance(self):
        if self._instance != None:
            self._releaseInstance(self._instance)
        
    def __init__(self):
        try:
            self.initVar()
        except:
            pass

    def __del__(self):
        self.releaseInstance()

    def linkDll(self):
        rootPath = os.path.dirname(__file__)
        dllPath = os.path.join(rootPath, "libavcombine.dll")
        self.dllInvoker = ctypes.WinDLL(dllPath)

    def initReturnBoolFunc(func):
        func.argtypes = [ctypes.c_void_p]
        func.restype = ctypes.c_bool

    def initStringParamFunc(func):
        func.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    def initReturnLongFunc(func):
        func.argtypes = [ctypes.c_void_p]
        func.restype = ctypes.c_int64

    def initCallbackFunc(func):
        func.argtypes = [ctypes.c_void_p, ctypes.CFUNCTYPE(
            ctypes.c_void_p, ctypes.c_int64)]

    def initFunction(self):
        self._getInstance = self.dllInvoker.getInstance
        self._getInstance.restype = ctypes.c_void_p

        self._releaseInstance = self.dllInvoker.releaseInstance
        self._releaseInstance.argtypes = [ctypes.c_void_p]

        self._setAudio = self.dllInvoker.setAudio
        AVCombine.initStringParamFunc(self._setAudio)

        self._setVideo = self.dllInvoker.setVideo
        AVCombine.initStringParamFunc(self._setVideo)

        self._setOutPath = self.dllInvoker.setOutPath
        AVCombine.initStringParamFunc(self._setOutPath)

        self._OpenStream = self.dllInvoker.OpenStream
        AVCombine.initReturnBoolFunc(self._OpenStream)

        self._WriteToFile = self.dllInvoker.WriteToFile
        AVCombine.initReturnBoolFunc(self._WriteToFile)

        self._getAudioFrame = self.dllInvoker.getAudioFrame
        AVCombine.initReturnLongFunc(self._getAudioFrame)

        self._getVideoFrame = self.dllInvoker.getVideoFrame
        AVCombine.initReturnLongFunc(self._getVideoFrame)

        self._setCallbackAudio = self.dllInvoker.setCallbackAudio
        AVCombine.initCallbackFunc(self._setCallbackAudio)

        self._setCallbackVideo = self.dllInvoker.setCallbackVideo
        AVCombine.initCallbackFunc(self._setCallbackVideo)

    def convertToCharPtr(str):
        ptr = ctypes.c_char_p(bytes(str, 'utf-8'))
        return ptr

    def setVideo(self, path):
        self._video = path
        self._videoPtr = AVCombine.convertToCharPtr(self._video)
        self._setVideo(self._instance, self._videoPtr)

    def setAudio(self, path):
        self._audio = path
        self._audioPtr = AVCombine.convertToCharPtr(self._audio)
        self._setAudio(self._instance, self._audioPtr)

    def setOutPath(self, path):
        self._out = path
        self._outPtr = AVCombine.convertToCharPtr(self._out)
        self._setOutPath(self._instance, self._outPtr)

    def OpenStream(self):
        result = self._OpenStream(self._instance)
        return result

    def WriteToFile(self):
        result = self._WriteToFile(self._instance)
        return result

    def getVideoFrame(self):
        result = self._getVideoFrame(self._instance)
        return result

    def getAudioFrame(self):
        result = self._getAudioFrame(self._instance)
        return result

    def setCallbackAudio(self, callback):
        self._callbackAudio = callback
        self._callbackAudioC = ctypes.CFUNCTYPE(
            ctypes.c_void_p, ctypes.c_int64)(callback)
        self._setCallbackAudio(self._instance, self._callbackAudioC)

    def setCallbackVideo(self, callback):
        self._callbackVideo = callback
        self._callbackVideoC = ctypes.CFUNCTYPE(
            ctypes.c_void_p, ctypes.c_int64)(callback)
        self._setCallbackVideo(self._instance, self._callbackVideoC)


def callback1(x):
    pass


def callback2(x):
    pass


def main():
    avcom = AVCombine()
    video = input("Video path:")
    audio = input("Audio path:")
    output = input("Output path:")
    avcom.setVideo(video)
    avcom.setAudio(audio)
    avcom.setOutPath(output)
    result = avcom.OpenStream()
    if result:
        print("Video %d frames,audio %s frames." %
              (avcom.getVideoFrame(), avcom.getAudioFrame()))
        avcom.setCallbackVideo(callback1)
        avcom.setCallbackAudio(callback2)
        result2 = avcom.WriteToFile()
        if result2:
            print("Success")
        else:
            print("WriteToFile failed")
    else:
        print("OpenStream failed")


if __name__ == '__main__':
    main()
