import ts3lib, ts3defines
from datetime import datetime
from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer
from bluscream import timestamp
from ts3defines import LogLevel

class antiServerKick(ts3plugin):
    name = "Anti Server Kick"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Auto rejoin servers after you got kicked."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = False
    whitelistUIDs = ["serveradmin"]
    delay = 2500
    tabs = {}
    schid = 0


    def log(self, logLevel, message, schid=0):
        ts3lib.logMessage(message, logLevel, self.name, schid)
        if logLevel in [LogLevel.LogLevel_DEBUG, LogLevel.LogLevel_DEVEL] and self.debug:
            ts3lib.printMessage(schid if schid else ts3lib.getCurrentServerConnectionHandlerID(), '{timestamp} [color=orange]{name}[/color]: {message}'.format(timestamp=timestamp(), name=self.name, message=message), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)

    def __init__(self):
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        (err, status) = ts3lib.getConnectionStatus(schid)
        if err == ts3defines.ERROR_ok and status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: self.saveTab(schid)
        self.log(LogLevel.LogLevel_DEBUG, "Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: self.saveTab(schid)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if schid not in self.tabs: return
        if clientID != self.tabs[schid]["clid"]: return
        # (err, pw) = ts3lib.getChannelVariable(schid, newChannelID, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
        (err, self.tabs[schid]["cpath"], self.tabs[schid]["cpw"]) = ts3lib.getChannelConnectInfo(schid, newChannelID)
        self.log(LogLevel.LogLevel_DEBUG, "Tab updated: {}".format(self.tabs[schid]), schid)

    def onClientSelfVariableUpdateEvent(self, schid, flag, oldValue, newValue):
        if flag != ts3defines.ClientProperties.CLIENT_NICKNAME: return
        if schid not in self.tabs: return
        self.tabs[schid]["nick"] = newValue
        self.log(LogLevel.LogLevel_DEBUG, "Tab updated: {}".format(self.tabs[schid]), schid)

    def onClientKickFromServerEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        self.log(LogLevel.LogLevel_DEBUG, "kicked")
        if kickerID == clientID: return
        if clientID != self.tabs[schid]["clid"]: return
        if kickerUniqueIdentifier in self.whitelistUIDs: return
        if schid not in self.tabs: return
        if self.delay > 0:
            self.schid = schid
            QTimer.singleShot(self.delay, self.reconnect)
        else: self.reconnect(schid)

    def saveTab(self, schid):
        if schid not in self.tabs:
            self.tabs[schid] = {}
        (err, self.tabs[schid]["name"]) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
        (err, self.tabs[schid]["host"], self.tabs[schid]["port"], self.tabs[schid]["pw"]) = ts3lib.getServerConnectInfo(schid)
        (err, self.tabs[schid]["clid"]) = ts3lib.getClientID(schid)
        (err, self.tabs[schid]["nick"]) = ts3lib.getClientDisplayName(schid, self.tabs[schid]["clid"])
        (err, cid) = ts3lib.getChannelOfClient(schid, self.tabs[schid]["clid"])
        (err, self.tabs[schid]["cpath"], self.tabs[schid]["cpw"]) = ts3lib.getChannelConnectInfo(schid, cid)
        self.log(LogLevel.LogLevel_DEBUG, "Saved Tab: {}".format(self.tabs[schid]), schid)

    def reconnect(self, schid=None):
        schid = schid if schid else self.schid
        self.log(LogLevel.LogLevel_DEBUG, "Reconnecting to tab: {0}".format(self.tabs[schid]))
        # ts3lib.startConnection
        ts3lib.guiConnect(ts3defines.PluginConnectTab.PLUGIN_CONNECT_TAB_CURRENT, self.tabs[schid]["name"],
                       '{}:{}'.format(self.tabs[schid]["host"], self.tabs[schid]["port"]) if hasattr(self.tabs[schid], 'port') else self.tabs[schid]["host"],
                        self.tabs[schid]["pw"],
                       self.tabs[schid]["nick"], self.tabs[schid]["cpath"], self.tabs[schid]["cpw"], "", "", "", "", "", "", "")
        self.schid = 0
