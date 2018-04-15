import ts3lib, ts3defines
from datetime import datetime
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from bluscream import timestamp, channelURL, clientURL
from random import randint

class antiMove(ts3plugin):
    name = "Anti Move"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Deny others to move you around."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Antimove", "")]
    hotkeys = []
    whitelistUIDs = ["serveradmin"]
    whitelistSGIDs = [2]
    delay = (250, 1500)
    backup = None

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_DISCONNECTED: return
        if self.backup is not None and hasattr(self.backup, "schid") and self.backup["schid"] == schid:
            self.backup = None

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            if self.backup is None:
                self.backup = {}
                ts3lib.printMessageToCurrentTab("{}[color=green]Enabled[/color] {}".format(timestamp(),self.name))
            else:
                self.backup = None
                ts3lib.printMessageToCurrentTab("{}[color=red]Disabled[/color] {}".format(timestamp(),self.name))

    def onClientMoveMovedEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
        if moverID == 0 or self.backup is None: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID or moverID == ownID or moverID == 0: return
        (err, sgids) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        if not set(sgids).isdisjoint(self.whitelistSGIDs): return
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if uid in self.whitelistUIDs: return
        self.backup = {"schid": schid, "cid": oldChannelID}
        delay = randint(self.delay[0], self.delay[1])
        ts3lib.printMessageToCurrentTab("{} {}: Switching back to channel {} in {}ms".format(timestamp(),self.name,channelURL(schid, self.backup["cid"]), delay))# clientURL(schid, self.backup["schid"]), 
        QTimer.singleShot(delay, self.moveBack)

    def moveBack(self):
        if self.backup is None: return
        (err, ownID) = ts3lib.getClientID(self.backup["schid"])
        (err, path, pw) = ts3lib.getChannelConnectInfo(self.backup["schid"], self.backup["cid"])
        ts3lib.requestClientMove(self.backup["schid"], ownID, self.backup["cid"], pw)
        self.backup = {}
