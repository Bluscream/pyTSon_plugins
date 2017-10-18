import ts3lib, ts3defines
from datetime import datetime
from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer


class antiMove(ts3plugin):
    name = "Anti Move"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Deny others to move you around."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Antimove", "")]
    hotkeys = []
    enabled = False
    debug = True
    whitelistUIDs = [""]
    whitelistSGIDs = [2]
    delay = 0
    schid=0;clid=0;cid=0;cpw="123"

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def log(self, logLevel, message, schid=0):
        ts3lib.logMessage(message, logLevel, self.name, schid)
        if logLevel in [ts3defines.LogLevel.LogLevel_DEBUG, ts3defines.LogLevel.LogLevel_DEVEL] and self.debug:
            ts3lib.printMessage(schid if schid else ts3lib.getCurrentServerConnectionHandlerID(), '{timestamp} [color=orange]{name}[/color]: {message}'.format(timestamp=self.timestamp(), name=self.name, message=message), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            self.enabled = not self.enabled
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.enabled))

    def onClientMoveMovedEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
        self.log(ts3defines.LogLevel.LogLevel_DEBUG, "moverID == 0: {}".format(moverID == 0), schid)
        if moverID == 0: return
        (err, ownID) = ts3lib.getClientID(schid)
        self.log(ts3defines.LogLevel.LogLevel_DEBUG, "clientID != ownID: {} OR moverID == ownID: {}".format(clientID != ownID, moverID == ownID), schid)
        if clientID != ownID or moverID == ownID: return
        (err, sgids) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        self.log(ts3defines.LogLevel.LogLevel_DEBUG, "set(sgids).isdisjoint(self.whitelistSGIDs): {}".format(set(sgids).isdisjoint(self.whitelistSGIDs)), schid)
        if not set(sgids).isdisjoint(self.whitelistSGIDs): return
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        self.log(ts3defines.LogLevel.LogLevel_DEBUG, "uid in self.whitelistUIDs: {}".format(uid in self.whitelistUIDs), schid)
        if uid in self.whitelistUIDs: return
        self.schid=schid;self.clid=ownID;self.cid=oldChannelID
        (err, cpath, self.cpw) = ts3lib.getChannelConnectInfo(schid, oldChannelID)
        if self.delay >= 0: QTimer.singleShot(self.delay, self.moveBack)
        else: self.moveBack()


    def moveBack(self):
        ts3lib.requestClientMove(self.schid, self.clid, self.cid, self.cpw)