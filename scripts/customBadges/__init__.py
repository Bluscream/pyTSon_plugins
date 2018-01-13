from ts3plugin import ts3plugin
from random import choice, getrandbits
from PythonQt.QtCore import QTimer, Qt, QUrl
from PythonQt.QtGui import QWidget, QListWidgetItem, QIcon, QPixmap
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from bluscream import *
from os import path
from configparser import ConfigParser
from pytson import getPluginPath
from pytsonui import setupUi
from json import load, loads
import ts3defines, ts3lib

class customBadges(ts3plugin):
    name = "Custom Badges"
    apiVersion = 21
    requestAutoload = True
    version = "0.9"
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
        try:
            with open(self.badgesinfo, encoding='utf-8-sig') as json_file:
                self.badges = load(json_file)
        except:
            self.nwmc = QNetworkAccessManager()
            self.nwmc.connect("finished(QNetworkReply*)", self.loadBadges)
            self.nwmc.get(QNetworkRequest(QUrl("https://gist.githubusercontent.com/Bluscream/29b838f11adc409feac9874267b43b1e/raw")))
        if self.cfg.getboolean("general", "debug"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def loadBadges(self, reply):
        data = reply.readAll().data().decode('utf-8')
        self.badges = loads(data)

    def stop(self):
        saveCfg(self.ini, self.cfg)

    def configure(self, qParentWidget):
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
        super(QWidget, self).__init__(parent)
        self.listen = False
        setupUi(self, customBadges.ui)
        self.cfg = customBadges.cfg
        self.badges = customBadges.badges
        self.setCustomBadges = customBadges.setCustomBadges
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Customize Badges")
        self.setupList()
        self.listen = True

    def badgeItem(self, badge, alt=False):
        item = QListWidgetItem(self.badges[badge]["name"])
        item.setData(Qt.UserRole, badge)
        item.setToolTip(self.badges[badge]["description"])
        item.setIcon(QIcon("{}\\{}{}".format(self.icons, self.badges[badge]["filename"],"_details" if alt else "")))
        return item

    def setupList(self):
        self.chk_overwolf.setChecked(True if self.cfg.getboolean('general', 'overwolf') else False)
        for badge in self.badges:
            self.lst_available.addItem(self.badgeItem(badge))
        badges = self.cfg.get('general', 'badges').split(",")
        if len(badges) < 1: return
        i = 0
        for badge in badges:
            if not badge: return
            i += 1
            if i == 1:
                self.badge1.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[badge]["filename"])))
            elif i == 2:
                self.badge2.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[badge]["filename"])))
            elif i == 3:
                self.badge3.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[badge]["filename"])))
            self.lst_active.addItem(self.badgeItem(badge))

    def updateBadges(self):
        items = []
        self.badge1.clear();self.badge2.clear();self.badge3.clear();
        for i in range(self.lst_active.count):
             uid = self.lst_active.item(index).data(Qt.UserRole)
             items.append(uid)
             if i == 0:
                 self.badge1.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[uid]["filename"])))
             elif i == 1:
                 self.badge2.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[uid]["filename"])))
             elif i == 2:
                 self.badge3.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[uid]["filename"])))
        self.cfg.set('general', 'badges', ','.join(items))
        self.setCustomBadges()


    def addActive(self):
        item = self.lst_available.currentItem()
        self.lst_active.addItem(self.badgeItem(item.data(Qt.UserRole)))
        self.updateBadges()

    def delActive(self):
        row = self.lst_active.currentRow
        self.lst_active.takeItem(row)
        self.updateBadges()

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
        if not self.listen: return
        self.updateBadges()

    def on_lst_active_itemChanged(self, mi):
        if not self.listen: return
        self.updateBadges()

    def on_btn_apply_clicked(self):
        if not self.listen: return
        self.updateBadges()

    def on_btn_close_clicked(self):
        self.close()
