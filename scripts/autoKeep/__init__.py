import ts3lib, ts3defines, datetime
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from random import randint
from bluscream import timestamp, clientURL, channelURL

class autoKeep(ts3plugin):
    name = "Auto Keep"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Auto keep someone around you."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Stop %s"%name, ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, name, "")
    ]
    hotkeys = []
    delay = (0, 0)
    targets = {}

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_DISCONNECTED: return
        if schid in self.targets: del self.targets[schid]

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID != 0: return
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if schid in self.targets:
                ts3lib.printMessageToCurrentTab("{} {}: [color=orange]No longer auto-dragging[/color] {}".format(timestamp(),self.name,clientURL(schid, self.targets[schid])))
                del self.targets[schid]
            else: ts3lib.printMessageToCurrentTab("{} {}: [color=red]Not dragging anyone on this tab.[/color]".format(timestamp(),self.name))
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            (err, ownID) = ts3lib.getClientID(schid)
            if selectedItemID == ownID: return
            self.targets[schid] = selectedItemID
            ts3lib.printMessageToCurrentTab("{} {}: [color=green]Now auto-dragging[/color] {}".format(timestamp(),self.name,clientURL(schid, selectedItemID)))
            self.dragTarget(schid)

    def dragTarget(self, schid = 0):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        (err, ownID) = ts3lib.getClientID(schid)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        clid = self.targets[schid]
        (err, cid) = ts3lib.getChannelOfClient(schid, clid)
        if ownCID == cid: return
        (err, path, pw) = ts3lib.getChannelConnectInfo(schid, ownCID)
        ts3lib.requestClientMove(schid, clid, ownCID, pw)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not schid in self.targets: return
        (err, ownID) = ts3lib.getClientID(schid)
        if not clientID in [ownID,self.targets[schid]] : return
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if newChannelID == ownCID: return
        delay = randint(self.delay[0], self.delay[1])
        ts3lib.printMessageToCurrentTab("{} {}: Auto-dragging {} in channel {} in {}ms".format(timestamp(),self.name,clientURL(schid, self.targets[schid]), channelURL(schid, newChannelID), delay))
        QTimer.singleShot(delay, self.dragTarget)