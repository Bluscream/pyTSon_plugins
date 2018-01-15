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
from traceback import format_exc
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
    infoTitle = "[b]Badges[/b]"
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Change " + name, "")]
    hotkeys = []
    icons = path.join(ts3lib.getConfigPath(), "cache", "badges")
    ini = path.join(getPluginPath(), "scripts", "customBadges", "settings.ini")
    ui = path.join(getPluginPath(), "scripts", "customBadges", "badges.ui")
    badges_local = path.join(getPluginPath(), "include", "badges.json")
    badges_remote = "https://gist.githubusercontent.com/Bluscream/29b838f11adc409feac9874267b43b1e/raw"
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
        try:
            loadCfg(self.ini, self.cfg)
            self.requestBadges()
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def infoData(self, schid, id, atype):
        if atype != ts3defines.PluginItemType.PLUGIN_CLIENT: return None
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID != id: return None
        # overwolf = self.cfg.getboolean('general', 'overwolf')
        # badges = self.cfg.get('general', 'badges').split(',')
        (err, badges) = ts3lib.getClientVariable(schid, ownID, ts3defines.ClientPropertiesRare.CLIENT_BADGES)
        (overwolf, badges) = parseBadges(badges)
        _return = ["Overwolf: {0}".format("[color=green]Yes[/color]" if overwolf else "[color=red]No[/color]")]
        for badge in badges:
            _return.append("{} {}".format(
                "[img]https://badges-content.teamspeak.com/{}/{}.svg[/img]".format(badge, self.badges[badge]["filename"] if badge in self.badges else "unknownw"),
                self.badgeNameByUID(badge) if badge in self.badges else badge
            ))
        return _return

    def badgeNameByUID(self, uid):
        for badge in self.badges:
            if badge == uid: return self.badges[badge]["name"]

    def requestBadges(self):
        try:
            with open(self.badges_local, encoding='utf-8-sig') as json_file:
                self.badges = load(json_file)
        except:
            self.nwmc = QNetworkAccessManager()
            self.nwmc.connect("finished(QNetworkReply*)", self.loadBadges)
            self.nwmc.get(QNetworkRequest(QUrl(self.badges_remote)))

    def loadBadges(self, reply):
        try:
            data = reply.readAll().data().decode('utf-8')
            self.badges = loads(data)
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{}".format(self.badges))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

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
        try:
            overwolf = self.cfg.getboolean('general', 'overwolf')
            badges = self.cfg.get('general', 'badges').split(",")
            if len(badges) > 0: badges += ['0c4u2snt-ao1m-7b5a-d0gq-e3s3shceript']
            sendCommand(self.name, buildBadges(badges, overwolf))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def openDialog(self):
        if not self.dlg: self.dlg = BadgesDialog(self)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

class BadgesDialog(QWidget):
    listen = False
    def __init__(self, customBadges, parent=None):
        try:
            super(QWidget, self).__init__(parent)
            setupUi(self, customBadges.ui)
            self.cfg = customBadges.cfg
            self.ini = customBadges.ini
            self.icons = customBadges.icons
            self.badges = customBadges.badges
            self.setCustomBadges = customBadges.setCustomBadges
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Customize Badges")
            self.setupList()
            self.listen = True
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def badgeItem(self, badge, alt=False):
        try:
            item = QListWidgetItem(self.badges[badge]["name"])
            item.setData(Qt.UserRole, badge)
            try: item.setToolTip(self.badges[badge]["description"])
            except: pass
            try: item.setIcon(QIcon("{}\\{}{}".format(self.icons, self.badges[badge]["filename"],"_details" if alt else "")))
            except: pass
            return item
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def updatePreview(self, uid, i):
        try:
            if i == 0:
                self.badge1.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[uid]["filename"])))
            elif i == 1:
                self.badge2.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[uid]["filename"])))
            elif i == 2:
                self.badge3.setPixmap(QPixmap("{}\\{}_details".format(self.icons, self.badges[uid]["filename"])))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def setupList(self):
        try:
            self.chk_overwolf.setChecked(True if self.cfg.getboolean('general', 'overwolf') else False)
            for badge in self.badges:
                self.lst_available.addItem(self.badgeItem(badge))
            badges = self.cfg.get('general', 'badges').split(",")
            if len(badges) < 1: return
            i = 0
            for badge in badges:
                if not badge: return
                if i < 3: self.updatePreview(badge, i)
                i += 1
                self.lst_active.addItem(self.badgeItem(badge))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def updateBadges(self):
        try:
            items = []
            self.badge1.clear();self.badge2.clear();self.badge3.clear();
            for i in range(self.lst_active.count):
                 uid = self.lst_active.item(i).data(Qt.UserRole)
                 items.append(uid)
                 if i < 3: self.updatePreview(uid, i)
            self.cfg.set('general', 'badges', ','.join(items))
            self.setCustomBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)


    def addActive(self):
        try:
            item = self.lst_available.currentItem()
            self.lst_active.addItem(self.badgeItem(item.data(Qt.UserRole)))
            self.updateBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def delActive(self):
        try:
            row = self.lst_active.currentRow
            self.lst_active.takeItem(row)
            self.updateBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

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
        try:
            self.cfg.set('general', 'overwolf', "True" if mi == Qt.Checked else "False")
            self.updateBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_lst_active_indexesMoved(self, mi):
        if not self.listen: return
        self.updateBadges()

    def on_lst_active_itemChanged(self, mi):
        if not self.listen: return
        self.updateBadges()

    def on_btn_apply_clicked(self):
        if not self.listen: return
        self.updateBadges()

    def on_btn_save_clicked(self):
        if not self.listen: return
        saveCfg(self.ini, self.cfg)

    def on_btn_close_clicked(self):
        self.close()
