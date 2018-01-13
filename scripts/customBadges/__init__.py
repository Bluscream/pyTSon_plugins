from ts3plugin import ts3plugin
from random import choice, getrandbits
from PythonQt.QtCore import QTimer, Qt
from PythonQt.QtGui import QWidget, QListWidgetItem, QIcon
from bluscream import *
from os import path
from configparser import ConfigParser
from pytson import getPluginPath
from pytsonui import setupUi
from json import load
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
    badgesinfo = path.join(getPluginPath(), "include", "badges.json")
    cfg = ConfigParser()
    dlg = None
    cfg["general"] = {
        "cfgversion": "1",
        "debug": "False",
        "enabled": "True",
        "badges": "",
        "overwolf": "False",
    }
    badges = {}

    def __init__(self):
        loadCfg(self.ini, self.cfg)
        with open(self.badgesinfo, encoding='utf-8-sig') as json_file:
            self.badges = load(json_file)
        if self.cfg.getboolean("general", "debug"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        saveCfg(self.ini, self.cfg)

    def configure(self, qParentWidget):
        """
        print("<configure>")
        print(self.cfg)
        if hasattr(self.cfg, "sections"):
            print(self.cfg.sections())
            print(self.cfg.get('general', 'badges'))
        print("</configure>")
        """
        self.openDialog()

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        self.openDialog()

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.setCustomBadges()

    def setCustomBadges(self):
        overwolf = self.cfg.getboolean('general', 'overwolf')
        badges = self.cfg.get('general', 'badges').split(",")
        sendCommand(self.name, buildBadges(badges, overwolf))

    def openDialog(self):
        if not self.dlg: self.dlg = BadgesDialog(self)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

class BadgesDialog(QWidget):
    listen = False
    icons = path.join(ts3lib.getConfigPath(), "cache", "badges")
    def __init__(self, customBadges, parent=None):
        try:
            super(QWidget, self).__init__(parent)
            setupUi(self, customBadges.ui)
            self.cfg = customBadges.cfg
            self.badges = customBadges.badges
            self.setCustomBadges = customBadges.setCustomBadges
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Customize Badges")
            self.setupList()
            self.listen = True
            # self.resize(1000, 600)
        except:
            try: from traceback import format_exc;ts3lib.logMessage("Custom Badges: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("Custom Badges: "+format_exc())
                except: print("Custom Badges: Unknown Error")

    def setupList(self):
        try:
            self.chk_overwolf.setChecked(True if self.cfg.getboolean('general', 'overwolf') else False)
            for k, v in ClientBadges.items():
                item = QListWidgetItem(k)
                item.setData(Qt.UserRole, v)
                item.setIcon(QIcon("{}\\{}".format(self.icons, self.badges[v]["filename"])))
                self.lst_available.addItem(item)
            badges = self.cfg.get('general', 'badges').split(",")
            print("badges; {}".format(badges))
            for badge in badges:
                item = QListWidgetItem(badgeNameByUID(badge))
                item.setData(Qt.UserRole, badge)
                item.setIcon(QIcon("{}\\{}_details".format(self.icons, self.badges[badge]["filename"])))
                self.lst_active.addItem(item)
        except:
            try: from traceback import format_exc;ts3lib.logMessage("Custom Badges: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("Custom Badges: "+format_exc())
                except: print("Custom Badges: Unknown Error")

    def updateBadges(self):
        items = []
        for index in range(self.lst_active.count):
             uid = self.lst_active.item(index).data(Qt.UserRole)
             items.append(uid)
             if index == 0:
                 self.badge1.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[uid]["filename"])))
             elif index == 1:
                 self.badge2.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[uid]["filename"])))
             elif index == 2:
                 self.badge3.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[uid]["filename"])))
        print("overwriting badges")
        self.cfg.set('general', 'badges', ','.join(items))
        self.setCustomBadges()


    def addActive(self):
        try:
            item = self.lst_available.currentItem()
            uid = item.data(Qt.UserRole)
            item = QListWidgetItem(item.text())
            item.setData(Qt.UserRole, uid)
            item.setIcon(QIcon("{}\\{}_details".format(self.icons, self.badges[uid]["filename"])))
            self.lst_active.addItem(item)
            self.updateBadges()
        except:
            try: from traceback import format_exc;ts3lib.logMessage("Custom Badges: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("Custom Badges: "+format_exc())
                except: print("Custom Badges: Unknown Error")

    def delActive(self):
        try:
            row = self.lst_active.currentRow
            self.lst_active.takeItem(row)
            self.updateBadges()
        except:
            try: from traceback import format_exc;ts3lib.logMessage("Custom Badges: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("Custom Badges: "+format_exc())
                except: print("Custom Badges: Unknown Error")

    def on_lst_available_doubleClicked(self, mi):
        if not self.listen: return
        self.addActive()

    def on_btn_addactive_clicked(self):
        if not self.listen: return
        self.addActive()

    def on_lst_active_doubleClicked(self, mi):
        if not self.listen: return
        self.delActive()

    def on_btn_removeactive_clicked(self):
        if not self.listen: return
        self.delActive()

    def on_chk_overwolf_stateChanged(self, mi):
        if not self.listen: return
        self.cfg.set('general', 'overwolf', "True" if mi == Qt.Checked else "False")
        self.updateBadges()

    def on_lst_active_indexesMoved(self, mi):
        self.updateBadges()

    def on_lst_active_itemChanged(self, mi):
        self.updateBadges()
