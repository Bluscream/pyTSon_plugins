import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtSql import QSqlDatabase
from pytson import getPluginPath, getCurrentApiVersion
from traceback import format_exc
from bluscream import *
from pytsonui import *
from PythonQt.QtCore import Qt
from PythonQt.QtGui import QWidget
from os import path

class channelGroupManager(ts3plugin):
    name = "Channel Group Manager"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Manage Members", "")]
    hotkeys = []
    dbpath = path.join(getPluginPath(), "scripts", "channelGroupManager", "members.db")
    ui = path.join(getPluginPath(), "scripts", "channelGroupManager", "members.ui")
    dlg = None
    cgroups = {}
    requested = False

    def __init__(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE", "channelGroupManager")
        self.db.setDatabaseName(self.dbpath)
        if not self.db.isValid(): raise Exception("Database invalid")
        if not self.db.open(): raise Exception("Could not open database.")
        self.loadVars()
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def loadVars(self, schid=False):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        self.cgroups[schid] = {"groups": {}}
        self.requested = True
        ts3lib.requestChannelGroupList(schid)
        ts3lib.requestServerVariables(schid)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHING:
            self.loadVars(schid)
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if schid in self.cgroups: del self.cgroups[schid]

    def onServerUpdatedEvent(self, schid):
        if not self.requested: return
        (err, dcgid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
        self.cgroups[schid]["default"] = dcgid

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL or menuItemID != 0: return
        if not self.dlg: self.dlg = channelGroupMembersDialog(self, schid, selectedItemID)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

    def onChannelGroupListEvent(self, schid, cgid, name, atype, iconID, saveDB):
        if not self.requested: return
        if atype == GroupType.TEMPLATE: return
        self.cgroups[schid]["groups"][cgid] = {}
        self.cgroups[schid]["groups"][cgid]["name"] = name
        self.cgroups[schid]["groups"][cgid]["icon"] = iconID

    def onChannelGroupListFinishedEvent(self, schid):
        if self.requested: self.requested = False

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        if channelGroupID == self.cgroups[schid]["default"]: return
        (err, uid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        query = "CREATE TABLE IF NOT EXISTS `{}|{}` (`NAME` TEXT, `UID` TEXT, `DBID` INTEGER, `CGID` INTEGER);".format(uid, channelID)
        d = self.db.exec_(query)
        print(query, ":", d)
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        (err, dbid) = ts3lib.getClientVariableAsInt(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        query = "INSERT INTO `{}|{}` (NAME, UID, DBID, CGID) VALUES (`{}`, `{}`, {}, {})".format(uid, channelID, uid, dbid, channelGroupID) # TODO: https://stackoverflow.com/a/4330694
        self.db.exec_(query)


class channelGroupMembersDialog(QWidget): # TODO: https://stackoverflow.com/questions/1332110/selecting-qcombobox-in-qtablewidget
    def __init__(self, channelGroupManager, schid, cid, parent=None):
        try:
            super(QWidget, self).__init__(parent)
            setupUi(self, channelGroupManager.ui)
            self.db = channelGroupManager.db
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Channel Group Members")
            self.setupTable(schid, cid, channelGroupManager.cgroups[schid])
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def setupTable(self, schid, cid, cgroups):
        pass

    def on_btn_close_clicked(self):
        self.close()

