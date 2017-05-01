import ts3defines, ts3lib
from pytson import getPluginPath
from ts3plugin import ts3plugin, PluginHost
from os import path
from datetime import datetime
from PythonQt.QtGui import QDialog, QWidget, QListWidgetItem
from PythonQt.QtCore import Qt
from pytsonui import setupUi

class channelGroupChanger(ts3plugin):
    name = "Channel Group Changer"
    import pytson;apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Change Channelgroup of clients that are not in the target channel.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Set as target channel", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Change Channel Group", "")]
    hotkeys = []
    debug = False
    toggle = True
    channel = 0
    dlg = None
    groups = {}


    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        self.requested = True ;ts3lib.requestChannelGroupList(ts3lib.getCurrentServerConnectionHandlerID())
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL:
            if menuItemID == 0:
                self.channel = selectedItemID
                ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())+" Set target channel to [color=yellow]"+str(self.channel)+"[/color]")
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            if menuItemID == 0:
                if self.channel == 0:
                    (e, ownID) = ts3lib.getClientID(schid)
                    (e, self.channel) = ts3lib.getChannelOfClient(schid, ownID)
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
        self.groups[channelGroupID] = name

    def onChannelGroupListFinishedEvent(self, schid):
        if self.requested: self.requested = False

class ChannelGroupDialog(QDialog): # https://raw.githubusercontent.com/pathmann/pyTSon/68c3a081e3aa27f055c902b092f1b31cc9b721d7/ressources/pytsonui.py
    def __init__(self, schid, cgid, dbid, name, channel, groups, parent=None):
        try:
            super(QDialog, self).__init__(parent)
            setupUi(self, path.join(getPluginPath(), "pyTSon", "scripts", "channelGroupChanger", "channelGroupSelect.ui"))
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle(name)
            # self.channelGroups.addItems(list(groups.values()))
            self.channelGroups.clear()
            for key,p in groups.items():
                try:
                    item = QListWidgetItem(self.channelGroups)
                    item.setText(p)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item.setCheckState(Qt.Checked if key == cgid else Qt.Unchecked)
                    item.setData(Qt.UserRole, key)
                    # item.setIcon(icon)
                except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            # self.channelGroups.sortItems()
            self.channelGroups.connect("itemChanged(QListWidgetItem*)", self.onSelectedChannelGroupChangedEvent)
            self.schid = schid;self.dbid = dbid;self.channel = channel
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
