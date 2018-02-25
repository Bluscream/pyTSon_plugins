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
import time

class channelGroupManager(ts3plugin):
    name = "Channel Group Manager"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream, shitty720"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle {}".format(name), ""), (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Manage Members", "")]
    hotkeys = []
    dbpath = path.join(getPluginPath(), "scripts", "channelGroupManager", "members.db")
    ui = path.join(getPluginPath(), "scripts", "channelGroupManager", "members.ui")
    dlg = None
    cgroups = {}
    requestedCGroups = False
    requestedRVars = False
    toggle = False

    def __init__(self):
        # if not self.toggle: self.stop(); return
        self.db = QSqlDatabase.addDatabase("QSQLITE", self.__class__.__name__)
        self.db.setDatabaseName(self.dbpath)
        if not self.db.isValid(): raise Exception("Database invalid")
        if not self.db.open(): raise Exception("Could not open database.")
        self.loadVars()
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]Bluscream[/url] loaded.".format(timestamp(), self.name, self.author))

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
        (err, acgid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_ADMIN_GROUP)
        self.cgroups[schid]["default"] = dcgid;self.cgroups[schid]["admin"] = acgid
        print(self.name, ">", "new default channel group for #", schid, ":", dcgid)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID != 0: return
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL:
            if not self.dlg: self.dlg = channelGroupMembersDialog(self, schid, selectedItemID)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            self.toggle = not self.toggle
            ts3lib.printMessageToCurrentTab("{} set to [color=orange]{}[/color]".format(self.name, self.toggle))

    def onChannelGroupListEvent(self, schid, cgid, name, atype, iconID, saveDB):
        if not self.requestedCGroups: return
        if atype == GroupType.TEMPLATE: return
        self.cgroups[schid]["groups"][cgid] = {}
        self.cgroups[schid]["groups"][cgid]["name"] = name
        self.cgroups[schid]["groups"][cgid]["icon"] = iconID
        print(self.name, ">", "new channelgroup for #", schid, "(", cgid, ")", ":", self.cgroups[schid]["groups"][cgid])

    def onChannelGroupListFinishedEvent(self, schid):
        if self.requestedCGroups: self.requestedCGroups = False

    def dbInsert(self, schid, cid, clid, cgid, dbid=None, invokerName="", invokerUID=""):
        print("got clid:", clid)
        for v in [schid, cid, clid, cgid]:
            if v is None: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        uuid = "{}|{}".format(suid, cid)
        self.execSQL("CREATE TABLE IF NOT EXISTS `{}` (`TIMESTAMP` NUMERIC, `NAME` TEXT, `UID` TEXT, `DBID` NUMERIC UNIQUE, `CGID` NUMERIC, `INVOKERNAME` TEXT, `INVOKERUID` TEXT);".format(uuid))
        (err, name) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        (err, uid) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if dbid is None: (err, dbid) = ts3lib.getClientVariableAsInt(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        q = "INSERT OR REPLACE INTO '{}' (TIMESTAMP, NAME, UID, DBID, CGID, INVOKERNAME, INVOKERUID) VALUES ({}, '{}', '{}', {}, {}, '{}', '{}')".format(uuid, int(time.time()), name, uid, dbid, cgid, invokerName, invokerUID)
        self.execSQL(q)

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        if not self.toggle: return
        if invokerClientID == 0: return
        print(self.name, ">", "channelGroupID:", channelGroupID, "channelID:", channelID, "clientID:", clientID, "invokerClientID:", invokerClientID, "invokerName:", invokerName, "invokerUniqueIdentity:", invokerUniqueIdentity)
        if not schid in self.cgroups: return
        # if not "default" in self.cgroups[schid]: return
        # if channelGroupID == self.cgroups[schid]["default"]: return # TODO: Maybe reimplement
        self.dbInsert(schid, channelID, clientID, channelGroupID, None, invokerName, invokerUniqueIdentity)

    def onNewChannelCreatedEvent(self, schid, cid, channelParentID, clid, invokerName, invokerUniqueIdentifier):
        if not self.toggle: return
        if not schid in self.cgroups: return
        self.dbInsert(schid, cid, clid, self.cgroups[schid]["admin"], None, "Server", "")

    def onDelChannelEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentifier):
        if not self.toggle: return
        if not schid in self.cgroups: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        self.execSQL("DROP TABLE IF EXISTS '{}|{}';".format(suid,channelID))

class channelGroupMembersDialog(QWidget): # TODO: https://stackoverflow.com/questions/1332110/selecting-qcombobox-in-qtablewidget
    def __init__(self, channelGroupManager, schid, cid, parent=None):
        try:
            super(QWidget, self).__init__(parent)
            setupUi(self, channelGroupManager.ui)
            self.schid = schid;self.cid = cid;self.cgroups = channelGroupManager.cgroups[schid]["groups"]
            self.db = channelGroupManager.db
            self.execSQL = channelGroupManager.execSQL
            self.setAttribute(Qt.WA_DeleteOnClose)
            (err, cname) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
            self.setWindowTitle("Members of \"{}\"".format(cname))
            self.tbl_members.setColumnWidth(0, 130)
            self.tbl_members.setColumnWidth(1, 250)
            self.tbl_members.setColumnWidth(2, 200)
            self.setupTable()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def setupTable(self):
        self.tbl_members.clearContents()
        self.tbl_members.setRowCount(0)
        cache = ts3client.ServerCache(self.schid)
        (err, suid) = ts3lib.getServerVariable(self.schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        q = self.execSQL("SELECT * FROM '{}|{}'".format(suid, self.cid))
        while q.next():
            pos = self.tbl_members.rowCount
            print(pos)
            self.tbl_members.insertRow(pos)
            self.tbl_members.setItem(pos, 0, QTableWidgetItem(datetime.utcfromtimestamp(q.value("timestamp")).strftime('%Y-%m-%d %H:%M:%S')))
            self.tbl_members.setItem(pos, 1, QTableWidgetItem(q.value("name")))
            self.tbl_members.setItem(pos, 2, QTableWidgetItem(q.value("uid")))
            self.tbl_members.setItem(pos, 3, QTableWidgetItem(str(q.value("dbid"))))
            box = QComboBox()
            box.connect("currentIndexChanged(int)", self.currentIndexChanged)
            i = 0
            for cgroup in self.cgroups:
                icon = QIcon(cache.icon(self.cgroups[cgroup]["icon"]))
                text = "{} ({})".format(self.cgroups[cgroup]["name"], cgroup)
                box.addItem(icon, text)
                box.setItemData(i, cgroup)
                if cgroup == q.value("cgid"): box.setCurrentIndex(i)
                i += 1
            self.tbl_members.setCellWidget(pos, 4, box)
            self.tbl_members.setItem(pos, 5, QTableWidgetItem("{} ({})".format(q.value("invokername"), q.value("INVOKERUID"))))

    def currentIndexChanged(self, i):
        print("test", i)
        row = self.tbl_members.currentRow()
        print("row:", row)
        # item = self.tbl_members.itemAt(const QPoint &point)
        # item = self.tbl_members.selectedItems()
        # print("item:", item)
        # self.tbl_members.at
        # ts3lib.requestSetClientChannelGroup(self.schid, [item.itemData], [self.channel], [self.dbid])

    def on_btn_close_clicked(self): self.close()

    def on_btn_reload_clicked(self): self.setupTable()