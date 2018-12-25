import ts3lib, ts3defines
from ts3plugin import ts3plugin
from bluscream import clientURL

class autoChannelKick(ts3plugin):
    name = "Auto Channel Kick"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, name, "")]
    hotkeys = []
    uid="";kicks=1

    def __init__(self): pass

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT: return
        if menuItemID != 0: return
        if self.uid:
            ts3lib.printMessageToCurrentTab("Disabled %s for %s"%(self.name,self.uid))
            self.uid = ""
        else:
            self.kicks = 1
            (err, self.uid) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            ts3lib.printMessageToCurrentTab("Enabled %s for %s"%(self.name,clientURL(schid, selectedItemID)))
            self.onClientMoveEvent(schid, selectedItemID,0,1,ts3defines.Visibility.RETAIN_VISIBILITY,"")

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.uid: return
        if not newChannelID: return
        if visibility != ts3defines.Visibility.RETAIN_VISIBILITY: return
        (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if uid != self.uid: return
        ts3lib.requestClientKickFromChannel(schid, clid, "Nope zum %sten"%self.kicks)
        self.kicks += 1