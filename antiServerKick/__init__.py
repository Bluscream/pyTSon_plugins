import ts3lib, ts3defines
from datetime import datetime
from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer


class antiServerKick(ts3plugin):
    name = "Anti Server Kick"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Auto rejoin servers after you got kicked."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Anti Server Kick", "")]
    hotkeys = []
    enabled = True
    debug = True
    whitelistUIDs = [""]
    whitelistSGIDs = [2]
    delay = 0
    tabs = {}
    schid = 0

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            self.enabled = not self.enabled
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.enabled))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.tabs[schid] = {}
            (err, self.tabs[schid]["name"]) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
            (err, self.tabs[schid]["host"], self.tabs[schid]["port"], self.tabs[schid]["pw"]) = ts3lib.getServerConnectInfo(schid)
            (err, clid) = ts3lib.getClientID(schid)
            (err, self.tabs[schid]["nick"]) = ts3lib.getClientDisplayName(schid, clid)
            (err, cid) = ts3lib.getChannelOfClient(schid, clid)
            (err, self.tabs[schid]["cpath"], self.tabs[schid]["cpw"]) = ts3lib.getChannelConnectInfo(schid, cid)

    def onClientKickFromServerEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        if kickerID == clientID: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID: return
        (err, sgids) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        if set(sgids).isdisjoint(self.whitelistSGIDs):
            if self.debug: ts3lib.printMessageToCurrentTab("Not reconnecting because kicker \"{}\" was in servergroup {}".format(kickerName, sgids))
            return
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if uid in self.whitelistUIDs:
            if self.debug: ts3lib.printMessageToCurrentTab("Not reconnecting because kicker \"{}\" has whitelisted UID {}".format(kickerName, uid))
            return
        if schid not in self.tabs:
            if self.debug: ts3lib.printMessageToCurrentTab("Not reconnecting because tab was not found!")
            return
        self.schid = schid
        if self.delay >= 0: QTimer.singleShot(self.delay, self.reconnect)
        else: self.reconnect(schid)


    def reconnect(self, schid=None):
        schid = schid or self.schid
        ts3lib.guiConnect(ts3defines.PluginConnectTab.PLUGIN_CONNECT_TAB_CURRENT, self.tabs[schid]["name"],
                       '{}:{}'.format(self.tabs[schid]["host"], self.tabs[schid]["port"]) if hasattr(self.tabs[schid], 'port') else self.tabs[schid]["host"],
                        self.tabs[schid]["pw"],
                       self.tabs[schid]["nick"], self.tabs[schid]["cpath"], self.tabs[schid]["cpw"], "", "", "", "", "", "", "")
        self.schid = 0
