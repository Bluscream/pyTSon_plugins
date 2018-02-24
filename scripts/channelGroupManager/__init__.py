import ts3lib, ts3defines, sip, copy
from ts3plugin import ts3plugin, PluginHost
from pytson import getPluginPath, getCurrentApiVersion
from traceback import format_exc
from bluscream import *
from pytsonui import setupUi
sip.setapi('QVariant', 2)
from PythonQt.QtCore import Qt# , QVariant
from PythonQt.QtSql import QSqlDatabase
from PythonQt.QtGui import QWidget, QTableWidgetItem, QComboBox, QIcon
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

    def execSQL(self, query):
        print(self.name, "> Query:", query)
        d = self.db.exec_(query)
        print(self.name, "> Result:", d)
        return d

    def purgeDB(self, schid):
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        (err, clist) = ts3lib.getChannelList(schid)
        d = self.execSQL("SELECT name FROM sqlite_master WHERE type='table'")
        drop = []
        while d.next():
            name = d.value("name").split('|')
            uid = name[0];cid = int(name[1])
            if uid != suid: continue
            print(self.name, "> CID:", cid)
            if not cid in clist: drop.append(cid)
        for cid in drop:
            name = "{}|{}".format(suid,cid)
            print(self.name, "> Deleting Table:", name)
            self.execSQL("DROP TABLE '{}';".format(name))

    def loadVars(self, schid=False):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        self.purgeDB(schid)
        # for cid in clist:
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
        if invokerClientID == 0: return
        print(self.name, ">", "channelGroupID:", channelGroupID, "channelID:", channelID, "clientID:", clientID, "invokerClientID:", invokerClientID, "invokerName:", invokerName, "invokerUniqueIdentity:", invokerUniqueIdentity)
        print(self.name, ">", "schid in self.cgroups:", schid in self.cgroups)
        if not schid in self.cgroups: return
        print(self.name, ">", "\"default\" in self.cgroups[schid]:", "default" in self.cgroups[schid])
        # print(self.name, ">", self.cgroups[schid])
        if not "default" in self.cgroups[schid]: return
        # print(self.name, ">", type(channelGroupID), channelGroupID, "==", type(self.cgroups[schid]["default"]), self.cgroups[schid]["default"])
        if channelGroupID == self.cgroups[schid]["default"]: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        uuid = "{}|{}".format(suid, channelID)
        d = self.execSQL("CREATE TABLE IF NOT EXISTS `{}` (`NAME` TEXT, `UID` TEXT, `DBID` INTEGER, `CGID` INTEGER);".format(uuid))
        (err, name) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        (err, dbid) = ts3lib.getClientVariableAsInt(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        # q = "INSERT INTO '{}' (NAME, UID, DBID, CGID) VALUES ('{}', '{}', {}, {})".format(uuid, name, uid, dbid, channelGroupID)
        # q = "INSERT OR REPLACE INTO '{0}' (NAME, UID, DBID, CGID) VALUES (  '{1}', '{2}', {3}, COALESCE((SELECT CGID FROM '{0}' WHERE DBID = {3}), {4});".format(uuid, name, uid, dbid, channelGroupID)
        q = "INSERT OR REPLACE INTO '{}' (NAME, UID, DBID, CGID) VALUES ('{}', '{}', {}, {})".format(uuid, name, uid, dbid, channelGroupID)
        self.execSQL(q)

    def onDelChannelEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentifier):
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        self.execSQL("DROP TABLE IF EXISTS '{}|{}';".format(suid,channelID))

class channelGroupMembersDialog(QWidget): # TODO: https://stackoverflow.com/questions/1332110/selecting-qcombobox-in-qtablewidget
    def __init__(self, channelGroupManager, schid, cid, parent=None):
        try:
            super(QWidget, self).__init__(parent)
            setupUi(self, channelGroupManager.ui)
            self.db = channelGroupManager.db
            self.execSQL = channelGroupManager.execSQL
            self.setAttribute(Qt.WA_DeleteOnClose)
            (err, cname) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
            self.setWindowTitle("Members of \"{}\"".format(cname))
            self.tbl_members.setColumnWidth(0, 250)
            self.tbl_members.setColumnWidth(1, 200)
            self.setupTable(schid, cid, channelGroupManager.cgroups[schid]["groups"])
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def setupTable(self, schid, cid, cgroups):
        self.tbl_members.clearContents()
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        q = self.execSQL("SELECT * FROM '{}|{}'".format(suid, cid))
        while q.next():
            box = QComboBox()
            i = 0
            for cgroup in cgroups:
                cache = ts3client.ServerCache(schid)
                icon = QIcon(cache.icon(cgroups[cgroup]["icon"]))
                text = "{} ({})".format(cgroups[cgroup]["name"], cgroup)
                box.addItem(icon, text)
                box.setItemData(i, cgroup)
                i += 1
            rowPosition = self.tbl_members.rowCount
            self.tbl_members.insertRow(rowPosition)
            self.tbl_members.setItem(rowPosition, 0, QTableWidgetItem(q.value(0)))
            self.tbl_members.setItem(rowPosition, 1, QTableWidgetItem(q.value(1)))
            self.tbl_members.setItem(rowPosition, 2, QTableWidgetItem(str(q.value(2))))
            if cgroup == q.value(3): box.setCurrentIndex(box.findData(cgroup))
            self.tbl_members.setCellWidget(rowPosition, 3, box) # str(q.value(3)))

    def on_btn_close_clicked(self):
        self.close()

