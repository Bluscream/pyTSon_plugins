import ts3lib, ts3defines
from datetime import datetime
from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer
from bluscream import intList

class antiChannelKick(ts3plugin):
    name = "Anti Channel Kick"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Auto rejoin channels you got kicked from."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Anti Channel Kick", "")]
    hotkeys = []
    enabled = False
    debug = False
    whitelistUIDs = [""]
    whitelistSGIDs = [2]
    delay = 0
    schid=0;clid=0;cid=0;cname="";cpw="123"

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            self.enabled = not self.enabled
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.enabled))

    def onClientKickFromChannelEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID or kickerID == ownID: return
        (err, sgids) = ts3lib.getClientVariableAsString(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        sgids = intList(sgids)
        if any(i in sgids for i in self.whitelistSGIDs): return
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if uid in self.whitelistUIDs: return
        (err, cpath, self.cpw) = ts3lib.getChannelConnectInfo(schid, oldChannelID)
        self.schid=schid;self.clid=ownID;self.cid=oldChannelID
        if self.delay >= 0: QTimer.singleShot(self.delay, self.moveBack)
        else: self.moveBack()

    def moveBack(self):
        ts3lib.requestClientMove(self.schid, self.clid, self.cid, self.cpw)
