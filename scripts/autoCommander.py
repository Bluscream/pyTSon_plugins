from ts3plugin import ts3plugin, PluginHost
import ts3, ts3defines, datetime


class autoCommander(ts3plugin):
    name = "Auto Channel Commander"
    apiVersion = 21
    requestAutoload = True
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
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug:
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.toggle = not self.toggle
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.datetime.now())+" Set Auto Channel Commander to [color=yellow]"+str(self.toggle)+"[/color]")

    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        if self.toggle:
            if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHING:
                self.requested = True
                ts3.requestChannelGroupList(ts3.getCurrentServerConnectionHandlerID())

    def onChannelGroupListEvent(self, serverConnectionHandlerID, channelGroupID, name, atype, iconID, saveDB):
        if self.toggle:
            if self.requested == True:
                for _name in self.mod_names:
                    if name.upper().__contains__(_name):
                        self.smgroup.extend([channelGroupID])

    def onChannelGroupListFinishedEvent(self, serverConnectionHandlerID):
        if self.toggle:
            self.requested = False

    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        if failedPermissionID == 184:
            return False;

    # def onClientMoveEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moveMessage):
    #     if self.toggle:
    #         schid = ts3.getCurrentServerConnectionHandlerID()
    #         (error, cID) = ts3.getClientID(schid)
    #         if error == ts3defines.ERROR_ok:
    #             if cID == clientID:
    #                 ts3.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
    #                 ts3.flushClientSelfUpdates(schid)
    #
    # def onClientMoveMovedEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
    #     if self.toggle:
    #         schid = ts3.getCurrentServerConnectionHandlerID()
    #         (error, cID) = ts3.getClientID(schid)
    #         if error == ts3defines.ERROR_ok:
    #             if cID == clientID:
    #                 ts3.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
    #                 ts3.flushClientSelfUpdates(schid)

    def onClientChannelGroupChangedEvent(self, serverConnectionHandlerID, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        if self.toggle:
            schid = ts3.getCurrentServerConnectionHandlerID()
            (error, cID) = ts3.getClientID(schid)
            if error == ts3defines.ERROR_ok:
                if cID == clientID:
                    (error, cgID) = ts3.getClientVariableAsInt(schid, cID, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
                    for _group in self.smgroup:
                        if cgID == _group:
                            ts3.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
                            ts3.flushClientSelfUpdates(schid)
                            break
