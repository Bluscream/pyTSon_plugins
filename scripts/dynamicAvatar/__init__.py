import ts3lib, ts3defines, random
from ts3plugin import ts3plugin
from configparser import ConfigParser
from os import path, remove, listdir
from shutil import copy2
from datetime import datetime
from pytsonui import setupUi
from base64 import b64encode
from hashlib import md5
from tempfile import gettempdir
from io import open as iopen#, BytesIO
from PythonQt.QtCore import QUrl, QIODevice, QFile, QTimer
from PythonQt.QtGui import QDialog, QFileDialog
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

class dynamicAvatar(ts3plugin):
    shortname = "PS"
    name = "Dynamic Avatar Changer"
    requestAutoload = False
    version = "1.0"
    import pytson;apiVersion = pytson.getCurrentApiVersion()
    author = "Bluscream"
    description = "Changes your avatar for you."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Refresh avatar", path.join(ts3lib.getPluginPath(),"pyTSon","scripts","dynamicAvatar","gfx","manual.png")),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Toggle Timer",'')]
    hotkeys = []
    ini = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "dynamicAvatar", "settings.ini")
    config = ConfigParser()
    timer = QTimer()
    int = 0

    def __init__(self):
        if path.isfile(self.ini): self.config.read(self.ini)
        else:
            self.config['GENERAL'] = { "debug": "False", "imgurl": "", "imgpath": "", "mode": "url", "refresh": "60" }
            with open(self.ini, 'w') as configfile: self.config.write(configfile)
        self.timer.timeout.connect(self.tick)
        ts3lib.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.config.getboolean('GENERAL','debug'): ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]Bluscream[/url] loaded.")
    def tick(self,schid=0):
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        self.int += 1;ts3lib.printMessageToCurrentTab('Tick %s'%self.int)
        if self.config['GENERAL']['mode'] == 'url': self.urlAvatar(schid)
        else: self.pathAvatar(schid)
    def configure(self, qParentWidget):
        try:
            self.dlg = SettingsDialog(self)
            self.dlg.show()
        except:
            from traceback import format_exc
            try: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon::"+self.name, 0)
            except: print("Error in "+self.name+".configure: "+format_exc())

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        try:
            if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
                if menuItemID == 0:
                    if self.config['GENERAL']['mode'] == "url": self.urlAvatar(schid)
                    elif self.config['GENERAL']['mode'] == "path": self.pathAvatar(schid)
                elif menuItemID == 1:
                    if self.timer.isActive() : self.timer.stop();ts3lib.printMessageToCurrentTab('Timer stopped!')
                    else: self.timer.start(int(self.config['GENERAL']['refresh'])*1000);ts3lib.printMessageToCurrentTab('Timer started!')
        except:
            try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except:
                try: from traceback import format_exc;print(format_exc())
                except: print("Unknown Error")


    def urlAvatar(self, schid):
        try:
            self.nwm = QNetworkAccessManager()
            self.nwm.connect("finished(QNetworkReply*)", self.onNetworkReply)
            self.schid = schid
            print("%s"%self.config['GENERAL']['imgurl'])
            self.nwm.get(QNetworkRequest(QUrl(self.config['GENERAL']['imgurl'])))
        except:
            from traceback import format_exc
            try: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except: print(format_exc())

    def onNetworkReply(self, reply): #http://stackoverflow.com/questions/41712636/qnetworkrequest-for-generated-images
        try:
            print("Error: %s (%s)"%(reply.error(), reply.errorString()))
            print("Content-Type: %s"%reply.header(QNetworkRequest.ContentTypeHeader))
            try: print("Content: %s"%reply.readAll())
            except: pass
            #if reply.header(QNetworkRequest.ContentTypeHeader) == "image/jpeg":
            imgraw = reply.readAll()#.data()#.decode('utf-8')
            temp_dir = gettempdir()
            filename = self.generateAvatarFileName(self.schid)
            tmp = path.join(temp_dir, filename)
            fn = QFile(tmp)
            fn.open(QIODevice.WriteOnly)
            fn.write(imgraw)
            fn.close
            #with open(tmp, 'wb') as f: f.write(imgraw)
            ts3lib.logMessage("Uploading %s as new avatar."%tmp, ts3defines.LogLevel.LogLevel_INFO, "PyTSon Script", 0)
            self.uploadAvatar(self.schid, tmp, filename)
        except:
            from traceback import format_exc
            try: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except: print(format_exc())
        reply.deleteLater()

    def pathAvatar(self, schid):
        try:
            _path = self.config['GENERAL']['imgpath']
            img = path.join(_path, random.choice([x for x in listdir(_path) if path.isfile(path.join(_path, x))]))
            if not self.getFileExtension(img) in ['bmp','gif','jpeg','jpg','pbm','pgm','png','ppm','xbm','xpm', None]: self.pathAvatar(schid);return
            temp_dir = gettempdir()
            filename = self.generateAvatarFileName(schid)
            tmp = path.join(temp_dir, filename)
            copy2(img, tmp)
            ts3lib.logMessage("Uploading %s as new avatar."%img, ts3defines.LogLevel.LogLevel_INFO, "PyTSon Script", 0)
            self.uploadAvatar(schid, tmp, filename)
        except:
            from traceback import format_exc
            try: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except: print(format_exc())

    def uploadAvatar(self, schid, img, filename=""):
        try:
            img = path.abspath(img)
            self.tmp = img
            if filename == "": filename = self.generateAvatarFileName(schid)
            imgdir = path.dirname(img)+path.sep
            self.retcode = ts3lib.createReturnCode()
            (error, ftid) = ts3lib.sendFile(schid, 0, "", "/avatar/"+filename, True, False, imgdir, self.retcode);
        except:
            try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except:
                try: from traceback import format_exc;print(format_exc())
                except: print("Unknown Error")

    def setAvatar(self, schid, img):
        ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientPropertiesRare.CLIENT_FLAG_AVATAR, self.getMd5FromFile(img))
        ts3lib.flushClientSelfUpdates(schid)

    def generateAvatarFileName(self, schid):
        (error, ownID) = ts3lib.getClientID(schid)
        (error, ownUID) = ts3lib.getClientVariableAsString(schid, ownID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        ownUID = ownUID.encode('ascii')
        return "avatar_"+b64encode(ownUID).decode("ascii").split('=')[0]

    def getMd5FromFile(self, file):
        hash_md5 = md5()
        with open(file, "rb") as f:
        #f = iopen(file, 'rb')
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        #f.close()
        return hash_md5.hexdigest()

    def getFileExtension(self, filename):
        basename = path.basename(filename)  # os independent
        ext = '.'.join(basename.split('.')[1:])
        return ext if ext else None

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if self.retcode == returnCode: self.retcode = None;self.setAvatar(schid, self.tmp)
        try: remove(self.tmp);self.tmp = None
        except: QTimer.singleShot(500, self.deltmp)


    def deltmp(self):
        try: f = iopen(self.tmp);f.close()
        except: pass
        try: remove(self.tmp);self.tmp = None
        except: QTimer.singleShot(1000, self.tmp)
    # def onFileTransferStatusEvent(self, ftid, status, statusMessage, remotefileSize, schid): # Doesn't work in pyTSon
    #     try:
    #         print("test")
    #         print(str("#"+ftid+": "+status))
    #     except:
    #         try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
    #         except:
    #             try: from traceback import format_exc;print(format_exc())
    #             except: print("Unknown Error")

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            if ts3lib.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER) == "QTRtPmYiSKpMS8Oyd4hyztcvLqU=": return
            if not self.timer.isActive(): self.timer.start(int(self.config['GENERAL']['refresh'])*1000);
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if self.timer.isActive(): self.timer.stop()

class SettingsDialog(QDialog):
    def buhl(self, s):
        if s.lower() == 'true' or s == 1: return True
        elif s.lower() == 'false' or s == 0: return False
        else: raise ValueError("Cannot convert {} to a bool".format(s))

    def __init__(self,Class,parent=None):
        self.dynamicAvatar=Class
        super(QDialog, self).__init__(parent)
        setupUi(self, path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "dynamicAvatar", "settings.ui"))
        s = Class.config["GENERAL"];b = self.buhl
        self.url.setChecked(s["mode"]=="url")
        self.path.setChecked(s["mode"]=="path")
        self.imgurl.setText(s["imgurl"])
        self.imgpath.setText(s["imgpath"])
        self.debug.setChecked(b(s["debug"]))
        self.refresh.setValue(int(s["refresh"]))

    def on_selectpath_clicked(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory);
        dialog.setOption(QFileDialog.ShowDirsOnly);
        result = dialog.getExistingDirectory(self, 'Choose Directory', path.curdir)
        if result: self.imgpath.setText(result)

    def on_apply_clicked(self):
        try:
            if self.url.isChecked(): self.dynamicAvatar.config.set("GENERAL", "mode", "url")
            else: self.dynamicAvatar.config.set("GENERAL", "mode", "path")
            self.dynamicAvatar.config.set("GENERAL", "debug", str(self.debug.isChecked()))
            self.dynamicAvatar.config.set("GENERAL", "refresh", str(self.refresh.value))
            self.dynamicAvatar.config.set("GENERAL", "imgurl", self.imgurl.text.replace('%', '%%'))
            self.dynamicAvatar.config.set("GENERAL", "imgpath", self.imgpath.text)
            with open(self.dynamicAvatar.ini, 'w') as configfile:
                self.dynamicAvatar.config.write(configfile)
        except:
            from traceback import format_exc
            try: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except: print(format_exc())

    def on_cancel_clicked(self):
        try: self.close()
        except: ts3lib.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
