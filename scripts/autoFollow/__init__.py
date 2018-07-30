import ts3lib, ts3defines, datetime
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from random import randint
from bluscream import timestamp, clientURL, channelURL, getChannelPassword

class autoFollow(ts3plugin):
    name = "Auto Follow (former Love Plugin)"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Auto Follow specified users around."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Stop Auto-Follow", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Auto-Follow", "")
    ]
    hotkeys = []
    delay = (250, 1500)
    targets = {}
    cid = 0

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_DISCONNECTED: return
        if schid in self.targets: del self.targets[schid]

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID != 0: return
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if schid in self.targets:
                ts3lib.printMessageToCurrentTab("{} {}: [color=orange]No longer auto-following[/color] {}".format(timestamp(),self.name,clientURL(schid, self.targets[schid])))
                del self.targets[schid]
            else: ts3lib.printMessageToCurrentTab("{} {}: [color=red]Not following anyone on this tab.[/color]".format(timestamp(),self.name))
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            (err, ownID) = ts3lib.getClientID(schid)
            if selectedItemID == ownID: return
            self.targets[schid] = selectedItemID
            ts3lib.printMessageToCurrentTab("{} {}: [color=green]Now auto-following[/color] {}".format(timestamp(),self.name,clientURL(schid, selectedItemID)))
            self.joinTarget(schid)

    def joinTarget(self, schid = 0, cid = 0):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        (err, ownID) = ts3lib.getClientID(schid)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if not cid: (err, cid) = ts3lib.getChannelOfClient(schid, self.targets[schid])
        if ownCID == cid: return
        pw = getChannelPassword(schid, cid, True)
        ts3lib.requestClientMove(schid, ownID, cid, pw if pw else "")
        self.cid = 0

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not schid in self.targets: return
        if self.targets[schid] != clientID: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID == ownID: return
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if newChannelID == ownCID: return
        delay = randint(self.delay[0], self.delay[1])
        ts3lib.printMessageToCurrentTab("{} {}: Auto-following {} in channel {} in {}ms".format(timestamp(),self.name,clientURL(schid, self.targets[schid]), channelURL(schid, newChannelID), delay))
        self.cid = newChannelID
        QTimer.singleShot(delay, self.joinTarget)

    def onClientMoveMovedEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
        if not schid in self.targets: return
        if self.targets[schid] != clientID: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID or moverID == ownID: return
        ts3lib.printMessageToCurrentTab("{} {}: [color=orange]No longer auto-following[/color] {} because we were moved!".format(timestamp(),self.name,clientURL(schid, self.targets[schid])))
        del self.targets[schid]
