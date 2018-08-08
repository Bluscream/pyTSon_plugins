import ts3lib, ts3defines, datetime
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from PythonQt.Qt import QApplication
from random import randint
from bluscream import timestamp, clientURL, channelURL, getChannelPassword, getClientIDByUID, inputBox, parseClientURL

class autoFollow(ts3plugin):
    name = "Auto Follow (former Love Plugin)"
    apiVersion = 22
    requestAutoload = False
    version = "1.1"
    author = "Bluscream"
    description = """Auto Follow specified users around. Supports several methods to read channel passwords.
    
    Required dependencies: https://github.com/Bluscream/pyTSon_plugins/blob/master/include/bluscream.py
    Recommended dependencies: https://github.com/Bluscream/pyTSon_plugins/tree/master/scripts/passwordCracker
    """
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

    def stop(self, reason=" because plugin was stopped", schid=0, target=0):
        ts3lib.printMessageToCurrentTab("{} {}: [color=orange]No longer auto-following[/color] {}{}!".format(timestamp(),self.name,clientURL(schid, target) if target else "anyone", reason))
        if schid and target != "anyone":
            del self.targets[schid]
        else:
            self.targets = {}

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_DISCONNECTED: return
        if schid in self.targets: del self.targets[schid]

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID != 0: return
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if schid in self.targets: self.stop("", schid, self.targets[schid])
            else:
                ts3lib.printMessageToCurrentTab("{} {}: [color=red]Not following anyone on this tab.[/color]".format(timestamp(),self.name))
                uid = inputBox(self.name, "UID:", QApplication.clipboard().text())
                parsed = parseClientURL(uid)
                if parsed: uid = parsed[1]
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            (err, ownID) = ts3lib.getClientID(schid)
            if selectedItemID == ownID: return
            (err, uid) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            if not uid:
                ts3lib.printMessageToCurrentTab(  "{} {}: [color=red]Cannot follow[/color] {}".format(timestamp(), self.name, selectedItemID))
                return
            self.targets[schid] = uid
            ts3lib.printMessageToCurrentTab("{} {}: [color=green]Now auto-following[/color] {}".format(timestamp(),self.name,clientURL(schid, selectedItemID)))
            if PluginHost.cfg.getboolean("general", "verbose"): print(self.name,"> self.targets[schid]",self.targets[schid],"selectedItemID",selectedItemID)
            self.joinTarget(schid)

    def onClientMoveMovedEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
        if not schid in self.targets: return
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.name,"onClientMoveMovedEvent > self.targets[schid]",self.targets[schid],"moverUniqueIdentifier",moverUniqueIdentifier)
        if self.targets[schid] != clientID: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID or moverID == ownID: return
        self.stop(" because we were moved", schid, clientID)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not schid in self.targets: return
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if err != ts3defines.ERROR_ok or not uid: return
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.name,"onClientMoveEvent > self.targets[schid]",self.targets[schid],"uid",uid)
        if self.targets[schid] != uid: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID == ownID: return
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if newChannelID == ownCID: return
        if newChannelID == 0 and visibility == ts3defines.Visibility.RETAIN_VISIBILITY:
            self.stop(" because he disconnected", schid, clientID); return
        self.join(schid, clientID, newChannelID)

    def onNewChannelCreatedEvent(self, schid, cid, channelParentID, invokerID, invokerName, invokerUniqueIdentifier):
        if not schid in self.targets: return
        (err, uid) = ts3lib.getClientVariable(schid, invokerID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if err != ts3defines.ERROR_ok or not uid: return
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.name,"onNewChannelCreatedEvent > self.targets[schid]",self.targets[schid],"uid",uid)
        if self.targets[schid] != uid: return
        self.join(schid, invokerID, cid)

    def check(self, schid, clid, cid): pass

    def join(self, schid, clid, cid):
        (err, ownID) = ts3lib.getClientID(schid)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if not cid: (err, cid) = ts3lib.getChannelOfClient(schid, self.targets[schid])
        if ownCID == cid: return
        delay = randint(self.delay[0], self.delay[1])
        ts3lib.printMessageToCurrentTab("{} {}: Auto-following {} in channel {} in {}ms".format(timestamp(), self.name, clientURL(schid, clid), channelURL(schid, cid), delay))
        self.cid = cid
        QTimer.singleShot(delay, self.joinTarget)

    def joinTarget(self, schid = 0, cid = 0):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        (err, ownID) = ts3lib.getClientID(schid)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        clid = getClientIDByUID(schid, self.targets[schid])
        if not cid: (err, cid) = ts3lib.getChannelOfClient(schid, clid)
        if ownCID == cid: return
        pw = getChannelPassword(schid, cid, True)
        ts3lib.requestClientMove(schid, ownID, cid, pw if pw else "")
        self.cid = 0