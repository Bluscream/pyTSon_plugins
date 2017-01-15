from ts3plugin import ts3plugin
from configparser import ConfigParser
from os import path
from datetime import datetime
from PythonQt.QtGui import QDialog, QFileDialog
from pytsonui import setupUi
import ts3lib, ts3defines

class dynamicAvatar(ts3plugin):
    shortname = "PS"
    name = "Dynamic Avatar Changer"
    requestAutoload = False
    version = "1.0"
    apiVersion = 21
    author = "Bluscream"
    description = "Changes your avatar for you."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Refresh avatar", path.join(ts3lib.getPluginPath(),"pyTSon","scripts","dynamicAvatar","gfx","manual.png"))]
    hotkeys = []
    ini = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "dynamicAvatar", "settings.ini")
    config = ConfigParser()

    def __init__(self):
        if path.isfile(self.ini): self.config.read(self.ini)
        else:
            self.config['GENERAL'] = { "debug": "False", "imgurl": "", "imgpath": "", "mode": "url", "refresh": "60" }
            with open(self.ini, 'w') as configfile: self.config.write(configfile)
        ts3lib.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.config.getboolean('GENERAL','debug'): ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]Bluscream[/url] loaded.")

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
                    if self.config['GENERAL']['mode'] == "url": self.urlAvatar()
                else: self.uploadAvatar(schid, "D:\\Users\\sysadmin\\Pictures\\amw\\1.png")
        except:
            try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except:
                try: from traceback import format_exc;print(format_exc())
                except: print("Unknown Error")


    def urlAvatar(self, schid):
        try: self.uploadAvatar(schid, avatar)
        except:
            from traceback import format_exc
            try: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except: print(format_exc())

    def pathAvatar(self):
        try:
            from os import listdir
            _path = self.config['GENERAL']['imgpath']
            files = [f for f in listdir(_path) if path.isfile(path.join(_path, f))]
            for f in files:
                 ts3lib.printMessageToCurrentTab(path.join(_path,f))
            self.uploadAvatar(schid, avatar)
        except:
            from traceback import format_exc
            try: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except: print(format_exc())

    def uploadAvatar(self, schid, image):
        try:
            (error, ownID) = ts3lib.getClientID(schid)
            (error, ownUID) = ts3lib.getClientVariableAsString(schid, ownID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            from base64 import b64encode
            ownUID = ownUID.encode('ascii')
            filename = "avatar_"+b64encode(ownUID).decode("ascii").split('=')[0]
            ts3lib.printMessageToCurrentTab(str(filename))
            (error, ftid) = ts3lib.sendFile(schid, 0, "", "/avatar", 1, 0, image);
            print("Started file transfer #"+str(ftid)+" with error code: "+str(error))
        except:
            try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except:
                try: from traceback import format_exc;print(format_exc())
                except: print("Unknown Error")

    def onFileTransferStatusEvent(self, ftid, status, statusMessage, remotefileSize, schid):
        try:
            print("test")
            print(str("#"+ftid+": "+status))
        except:
            try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Script", 0)
            except:
                try: from traceback import format_exc;print(format_exc())
                except: print("Unknown Error")

    def setAvatar(self, schid, flag):
        ts3lib.setClientSelfVariableAsString(serverConnectionHandlerID, CLIENT_FLAG_AVATAR, flag);

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
            self.dynamicAvatar.config.set("GENERAL", "imgurl", self.imgurl.text)
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
