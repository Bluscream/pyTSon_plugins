from ts3plugin import ts3plugin
from random import choice, getrandbits
from PythonQt.QtCore import QTimer, Qt
from PythonQt.QtGui import QWidget, QListWidgetItem
from bluscream import timestamp, sendCommand, calculateInterval, AntiFloodPoints, ClientBadges
from configparser import ConfigParser
from os import path, remove, listdir
from pytson import getPluginPath
from pytsonui import setupUi
import ts3defines, ts3lib

class customBadges(ts3plugin):
    name = "Custom Badges"
    apiVersion = 21
    requestAutoload = True
    version = "1"
    author = "Bluscream"
    description = "Automatically sets some badges for you :)"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Change " + name, "")]
    hotkeys = []
    ini = path.join(getPluginPath(), "scripts", "customBadges", "settings.ini")
    ui = path.join(getPluginPath(), "scripts", "customBadges", "badges.ui")
    cfg = ConfigParser()
    dlg = None
    cfg_default = {
        "cfgversion": "1",
        "debug": "False",
        "enabled": "True",
        "badges": ""
    }

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = self.cfg_default
            with open(self.ini, 'w') as cfg:
                self.cfg.write(cfg)
        if self.cfg.getboolean("general", "debug"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def configure(self, qParentWidget):
        self.openDialog()

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        self.openDialog()

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.setCustomBadges()

    def setCustomBadges():
        pass

    def buildBadges(self, badges, overwolf=False):
        return "clientupdate client_badges=overwolf={}:badges={}".format(1 if overwolf else 0, badges)

    def openDialog(self):
        if not self.dlg: self.dlg = BadgesDialog(self.cfg, self.ui)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

class BadgesDialog(QWidget):
    def __init__(self, cfg, ui, parent=None):
        try:
            super(QWidget, self).__init__(parent)
            setupUi(self, ui)
            self.cfg = cfg
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Customize Badges")
            self.setupList()
            # self.resize(1000, 600)
        except:
            try: from traceback import format_exc;ts3.logMessage("Custom Badges: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("Custom Badges: "+format_exc())
                except: print("Custom Badges: Unknown Error")

    def setupList(self):
        try:
            for k, v in ClientBadges:
                item = QListWidgetItem(k)
                item.setData(Qt.UserRole, v)
                # item.setIcon()
                self.lst_available.addItem(item)
        except:
            try: from traceback import format_exc;ts3.logMessage("Custom Badges: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("Custom Badges: "+format_exc())
                except: print("Custom Badges: Unknown Error")

    def addActive(self):
        try:
            item = self.lst_available.currentItem()
            self.lst_active.addItem(item)
        except:
            try: from traceback import format_exc;ts3.logMessage("Custom Badges: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("Custom Badges: "+format_exc())
                except: print("Custom Badges: Unknown Error")

    def delActive(self):
        try:
            item = self.lst_active.currentItem()
            self.lst_active.takeItem(item)
        except:
            try: from traceback import format_exc;ts3.logMessage("Custom Badges: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("Custom Badges: "+format_exc())
                except: print("Custom Badges: Unknown Error")

    def on_lst_available_doubleClicked(self, mi):
        self.addActive()

    def on_btn_addactive_clicked(self):
        self.addActive()

    def on_lst_active_doubleClicked(self, mi):
        self.delActive()

    def on_btn_removeactive_clicked(self):
        self.delActive()
