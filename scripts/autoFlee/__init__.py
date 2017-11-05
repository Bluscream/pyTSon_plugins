import ts3lib, ts3defines, datetime
from random import choice
from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer


class autoFlee(ts3plugin):
    name = "Auto Flee"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Deny others to move you around."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "AutoFlee", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "AutoFlee", "")]
    hotkeys = []
    enabled = False
    debug = False
    cids = []
    clids = []

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            self.enabled = not self.enabled
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.enabled))
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL and menuItemID == 0:
            if selectedItemID in self.cids: self.cids.remove(selectedItemID)
            else: self.cids.append(selectedItemID)
            ts3lib.printMessageToCurrentTab("{0} {1}> Channels to flee to: {2}".format(self.timestamp(), self.name, self.cids))
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT and menuItemID == 0:
            if selectedItemID in self.clids: self.clids.remove(selectedItemID)
            else: self.clids.append(selectedItemID)
            ts3lib.printMessageToCurrentTab("{0} {1}> Clients to flee from: {2}".format(self.timestamp(), self.name, self.cids))

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.enabled: return
        if not clientID in self.clids: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID == ownID: return
        (err, ownCID) = ts3lib.getChannelOfClient(schid, clientID)
        if newChannelID != ownCID: return
        chan = 0
        while chan <= 0 or chan == newChannelID:
            chan = choice(self.cids)
        ts3lib.requestClientMove(schid, ownID, chan, "123")