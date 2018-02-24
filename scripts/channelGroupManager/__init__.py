import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtSql import QSqlDatabase
from pytson import getPluginPath, getCurrentApiVersion
from traceback import format_exc
from bluscream import *
from pytsonui import setupUi
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
    requestedCGroups = False
    requestedRVars = False

    def __init__(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE", self.__class__.__name__)
        self.db.setDatabaseName(self.dbpath)
        if not self.db.isValid(): raise Exception("Database invalid")
        if not self.db.open(): raise Exception("Could not open database.")
        self.loadVars()
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        self.db.close()
        self.db.delete()
        QSqlDatabase.removeDatabase(self.__class__.__name__)

    def loadVars(self, schid=False):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        if schid in self.cgroups: return
        self.cgroups[schid] = {"groups": {}}
        self.requestedCGroups = True;self.requestedRVars = True
        ts3lib.requestChannelGroupList(schid)
        ts3lib.requestServerVariables(schid)
        print(self.name, ">", "requested vars for #", schid)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHING:
            self.loadVars(schid)
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if schid in self.cgroups: del self.cgroups[schid]

    def onServerUpdatedEvent(self, schid):
        if not self.requestedRVars: return
        self.requestedRVars = False
        (err, dcgid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
        self.cgroups[schid]["default"] = dcgid
        print(self.name, ">", "new default channel group for #", schid, ":", dcgid)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL or menuItemID != 0: return
        if not self.dlg: self.dlg = channelGroupMembersDialog(self, schid, selectedItemID)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

    def onChannelGroupListEvent(self, schid, cgid, name, atype, iconID, saveDB):
        if not self.requestedCGroups: return
        if atype == GroupType.TEMPLATE: return
        self.cgroups[schid]["groups"][cgid] = {}
        self.cgroups[schid]["groups"][cgid]["name"] = name
        self.cgroups[schid]["groups"][cgid]["icon"] = iconID
        print(self.name, ">", "new channelgroup for #", schid, "(", cgid, ")", ":", self.cgroups[schid]["groups"][cgid])

    def onChannelGroupListFinishedEvent(self, schid):
        if self.requestedCGroups: self.requestedCGroups = False

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        print(self.name, ">", "schid in self.cgroups:", schid in self.cgroups)
        if not schid in self.cgroups: return
        print(self.name, ">", "\"default\" in self.cgroups[schid]:", "default" in self.cgroups[schid])
        print(self.name, ">", self.cgroups[schid])
        if not "default" in self.cgroups[schid]: return
        print(self.name, ">", type(channelGroupID), channelGroupID, "==", type(self.cgroups[schid]["default"]), self.cgroups[schid]["default"])
        if channelGroupID == self.cgroups[schid]["default"]: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        query = "CREATE TABLE IF NOT EXISTS `{}|{}` (`NAME` TEXT, `UID` TEXT, `DBID` INTEGER, `CGID` INTEGER);".format(suid, channelID)
        d = self.db.exec_(query)
        print(self.name, "> Query:", query, "\nResult:", d)
        (err, name) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        (err, dbid) = ts3lib.getClientVariableAsInt(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        query = "INSERT INTO '{}|{}' (NAME, UID, DBID, CGID) VALUES ('{}', '{}', {}, {})".format(suid, channelID, name, uid, dbid, channelGroupID) # TODO: https://stackoverflow.com/a/4330694
        d = self.db.exec_(query)
        print(self.name, "> Query:", query, "\nResult:", d)

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

