import ts3defines, ts3lib
from ts3plugin import ts3plugin
from datetime import datetime


class autoCommander(ts3plugin):
    name = "Auto Channel Commander"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Automatically enable channel commander when switching channels.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Auto Channel Commander", "")]
    hotkeys = []
    debug = False
    toggle = True
    requested = False
    mod_names = ["ADMIN", "MOD", "OPERATOR"]
    smgroup = []

    def __init__(self):
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.toggle = not self.toggle
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.toggle))

    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        if not self.toggle: return
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHING:
            self.requested = True
            ts3lib.requestChannelGroupList(ts3lib.getCurrentServerConnectionHandlerID())

    def onChannelGroupListEvent(self, serverConnectionHandlerID, channelGroupID, name, atype, iconID, saveDB):
        if not self.toggle: return
        if self.requested == True:
            for _name in self.mod_names:
                if name.upper().__contains__(_name):
                    self.smgroup.extend([channelGroupID])

    def onChannelGroupListFinishedEvent(self, serverConnectionHandlerID):
        if self.toggle: self.requested = False

    # def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
         #if not self.toggle: return
#         (error, cID) = ts3lib.getClientID(schid)
#         if error == ts3defines.ERROR_ok:
#             if cID == clientID:
#                 ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
#                 ts3lib.flushClientSelfUpdates(schid)
    #
    # def onClientMoveMovedEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
    #     if not self.toggle: return
#         (error, cID) = ts3lib.getClientID(schid)
#         if error == ts3defines.ERROR_ok:
#             if cID == clientID:
#                 ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
#                 ts3lib.flushClientSelfUpdates(schid)

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        if not self.toggle: return
        (error, cID) = ts3lib.getClientID(schid)
        if error == ts3defines.ERROR_ok:
            if cID == clientID:
                (error, cgID) = ts3lib.getClientVariableAsInt(schid, cID, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
                for _group in self.smgroup:
                    if cgID == _group:
                        ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
                        ts3lib.flushClientSelfUpdates(schid)
                        break
