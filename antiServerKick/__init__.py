import ts3lib, ts3defines
from datetime import datetime
from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer
from ts3defines import LogLevel


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
    whitelistUIDs = ["serveradmin"]
    delay = 0
    tabs = {}
    schid = 0

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def log(self, logLevel, message, schid=0):
        ts3lib.logMessage(message, logLevel, self.name, schid)
        if logLevel in [LogLevel.LogLevel_DEBUG, LogLevel.LogLevel_DEVEL] and self.debug:
            ts3lib.printMessage(schid if schid else ts3lib.getCurrentServerConnectionHandlerID(), '{timestamp} [color=orange]{name}[/color]: {message}'.format(timestamp=self.timestamp(), name=self.name, message=message), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)

    def __init__(self):
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        (err, status) = ts3lib.getConnectionStatus(schid)
        if err == ts3defines.ERROR_ok and status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: self.saveTab(schid)
        self.log(LogLevel.LogLevel_DEBUG, "Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            self.enabled = not self.enabled
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.enabled))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.saveTab(schid)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if clientID != self.tabs[schid]["clid"]: return
        # (err, pw) = ts3lib.getChannelVariable(schid, newChannelID, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
        (err, self.tabs[schid]["cpath"], self.tabs[schid]["cpw"]) = ts3lib.getChannelConnectInfo(schid, newChannelID)
        self.log(LogLevel.LogLevel_DEBUG, "Tab updated: {}".format(self.tabs[schid]), schid)

    def onClientSelfVariableUpdateEvent(self, schid, flag, oldValue, newValue):
        if flag != ts3defines.ClientProperties.CLIENT_NICKNAME: return
        (err, self.tabs[schid]["nick"]) = newValue
        self.log(LogLevel.LogLevel_DEBUG, "Tab updated: {}".format(self.tabs[schid]), schid)

    def onClientKickFromServerEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        if kickerID == clientID:
            self.log(LogLevel.LogLevel_DEBUG, "Not reconnecting because kicker is target")
            return
        if clientID != self.tabs[schid]["clid"]:
            self.log(LogLevel.LogLevel_DEBUG, "Not reconnecting target is not self")
            return
        if kickerUniqueIdentifier in self.whitelistUIDs:
            self.log(LogLevel.LogLevel_DEBUG, "Not reconnecting because kicker \"{}\" has whitelisted UID {}".format(kickerName, uid))
            return
        if schid not in self.tabs:
            self.log(LogLevel.LogLevel_DEBUG, "Not reconnecting because tab was not found!")
            return
        self.schid = schid
        if self.delay >= 0: QTimer.singleShot(self.delay, self.reconnect)
        else: self.reconnect(schid)

    def saveTab(self, schid):
        if not hasattr(self.tabs, '%s'%schid):
            self.tabs[schid] = {}
        (err, self.tabs[schid]["name"]) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
        (err, self.tabs[schid]["host"], self.tabs[schid]["port"], self.tabs[schid]["pw"]) = ts3lib.getServerConnectInfo(schid)
        (err, self.tabs[schid]["clid"]) = ts3lib.getClientID(schid)
        (err, self.tabs[schid]["nick"]) = ts3lib.getClientDisplayName(schid, self.tabs[schid]["clid"])
        (err, cid) = ts3lib.getChannelOfClient(schid, self.tabs[schid]["clid"])
        (err, self.tabs[schid]["cpath"], self.tabs[schid]["cpw"]) = ts3lib.getChannelConnectInfo(schid, cid)
        self.log(LogLevel.LogLevel_DEBUG, "Saved Tab: {}".format(self.tabs[schid]), schid)

    def reconnect(self, schid=None):
        schid = schid or self.schid
        self.log(LogLevel.LogLevel_DEBUG, "Reconnecting to tab: {0}".format(self.tab[schid]))
        ts3lib.guiConnect(ts3defines.PluginConnectTab.PLUGIN_CONNECT_TAB_CURRENT, self.tabs[schid]["name"],
                       '{}:{}'.format(self.tabs[schid]["host"], self.tabs[schid]["port"]) if hasattr(self.tabs[schid], 'port') else self.tabs[schid]["host"],
                        self.tabs[schid]["pw"],
                       self.tabs[schid]["nick"], self.tabs[schid]["cpath"], self.tabs[schid]["cpw"], "", "", "", "", "", "", "")
        self.schid = 0
