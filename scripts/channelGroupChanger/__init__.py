import ts3defines, ts3lib
from pytson import getPluginPath
from ts3plugin import ts3plugin, PluginHost
from ts3client import ServerCache, IconPack
from os import path
from datetime import datetime
from PythonQt.QtGui import QInputDialog, QDialog, QListWidgetItem, QIcon, QLineEdit
from PythonQt.QtCore import Qt
from pytsonui import setupUi

class channelGroupChanger(ts3plugin):
    name = "Channel Group Changer"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Change Channelgroup of clients that are not in the target channel.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Set as target channel", ""),
				(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 1, "Change Channel Group", ""),
				(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Change Channel Group", "")
				]
    hotkeys = []
    debug = False
    toggle = True
    channel = 0
    dlg = None
    groups = {}


    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        self.requested = True ;ts3lib.requestChannelGroupList(ts3lib.getCurrentServerConnectionHandlerID())
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL:
            if menuItemID == 0:
                err, cname = ts3lib.getChannelVariable(schid, selectedItemID, ts3defines.ChannelProperties.CHANNEL_NAME)
                self.channel = selectedItemID, cname
                ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())+" Set target channel to [color=yellow]"+str(self.channel)+"[/color]")
            elif menuItemID == 1:
                (e, cgid) = ts3lib.getServerVariableAsUInt64(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
                x = QDialog()
                x.setAttribute(Qt.WA_DeleteOnClose)
                dbid = QInputDialog.getInt(x, "Manually change channel group", "Enter DBID", QLineEdit.Normal)
                if self.channel == 0:
                    (e, ownID) = ts3lib.getClientID(schid)
                    (e, cid) = ts3lib.getChannelOfClient(schid, ownID)
                    err, cname = ts3lib.getChannelVariable(schid, selectedItemID, ts3defines.ChannelProperties.CHANNEL_NAME)
                    self.channel = cid, cname
                name = "DBID: %s"%dbid
                if self.debug:
                    ts3lib.printMessageToCurrentTab("toggle: {0} | debug: {1} | channel: {2} | groups: {3} | dbid: {4} | name: {5}".format(self.toggle,self.debug,self.channel,self.groups,dbid,name))
                    ts3lib.printMessageToCurrentTab("schid: {0} | cgid: {1} | dbid: {2}".format(schid,cgid,dbid))
                if not self.dlg: self.dlg = ChannelGroupDialog(schid, cgid, dbid, name, self.channel, self.groups)
                self.dlg.show();self.dlg.raise_();self.dlg.activateWindow()
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            if menuItemID == 0:
                if self.channel == 0:
                    (e, ownID) = ts3lib.getClientID(schid)
                    (e, cid) = ts3lib.getChannelOfClient(schid, ownID)
                    err, cname = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
                    self.channel = cid, cname
                (e, dbid) = ts3lib.getClientVariableAsUInt64(schid, selectedItemID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                (e, cgid) = ts3lib.getClientVariableAsUInt64(schid, selectedItemID, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
                (e, name) = ts3lib.getClientVariableAsString(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_NICKNAME)
                if self.debug: ts3lib.printMessageToCurrentTab("toggle: {0} | debug: {1} | channel: {2} | groups: {3} | dbid: {4} | name: {5}".format(self.toggle,self.debug,self.channel,self.groups,dbid,name))
                if not self.dlg: self.dlg = ChannelGroupDialog(schid, cgid, dbid, name, self.channel, self.groups)
                self.dlg.show();self.dlg.raise_();self.dlg.activateWindow()

    def onChannelGroupListEvent(self, schid, channelGroupID, name, atype, iconID, saveDB):
        if not self.requested: return
        if self.debug: ts3lib.printMessageToCurrentTab("{name}: schid: {0} | channelGroupID: {1} | name: {2} | atype: {3} | iconID: {4} | saveDB: {5}".format(schid,channelGroupID,name,atype,iconID,saveDB,name=self.name))
        if not atype == 1: return
        if name in self.groups: return
        self.groups[channelGroupID] = [name, iconID]

    def onChannelGroupListFinishedEvent(self, schid):
        if self.requested: self.requested = False

class ChannelGroupDialog(QDialog): # https://raw.githubusercontent.com/pathmann/pyTSon/68c3a081e3aa27f055c902b092f1b31cc9b721d7/ressources/pytsonui.py
    def __init__(self, schid, cgid, dbid, name, channel, groups, parent=None):
        try:
            super(QDialog, self).__init__(parent)
            setupUi(self, path.join(getPluginPath(), "scripts", "channelGroupChanger", "channelGroupSelect.ui"))
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("\"{}\" | \"{}\"".format(name,channel[1]))
            cache = False
            try:
                icons = IconPack.current()
                icons.open()
                cache = ServerCache(schid)
            except: from traceback import format_exc;ts3lib.logMessage("Could not load icons: {}".format(format_exc()), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            # self.channelGroups.addItems(list(groups.values()))
            self.channelGroups.clear()
            for key,p in groups.items():
                try:
                    item = QListWidgetItem(self.channelGroups)
                    item.setText('{} ({})'.format(p[0], key))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item.setCheckState(Qt.Checked if key == cgid else Qt.Unchecked)
                    item.setData(Qt.UserRole, key)
                    if (cache):
                        try:
                            if p[1] == 0: continue;
                            elif p[1] in range(100, 700, 100):
                                item.setIcon(QIcon(IconPack.icon(icons,"group_{}".format(p[1]))))
                            else: item.setIcon(QIcon(ServerCache.icon(cache,p[1]&0xFFFFFFFF)))
                        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
                except: from traceback import format_exc;ts3lib.logMessage("Couldn't set icon: {}".format(format_exc()), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            icons.close()
            # self.channelGroups.sortItems()
            self.channelGroups.connect("itemChanged(QListWidgetItem*)", self.onSelectedChannelGroupChangedEvent)
            self.btn_set.connect("clicked(QPushButton*)", self.on_btn_set_clicked)
            self.schid = schid;self.dbid = dbid;self.channel = channel[0]
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0);pass

    def onSelectedChannelGroupChangedEvent(self, item):
        try:
            if item.checkState() == Qt.Checked:
                items = self.channelGroups.count
                for i in range(0,items):
                    litem = self.channelGroups.item(i);
                    if litem != item: litem.setCheckState(Qt.Unchecked)
                #ts3lib.printMessageToCurrentTab("channel: {0} | group: {1} | dbid: {2}".format(self.channel,item.data(Qt.UserRole),self.dbid))
                ts3lib.requestSetClientChannelGroup(self.schid, [item.data(Qt.UserRole)], [self.channel], [self.dbid])
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_btn_set_clicked(self):
        try:
            ts3lib.requestSetClientChannelGroup(self.schid, [self.spn_id.value], [self.channel], [self.dbid])
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)