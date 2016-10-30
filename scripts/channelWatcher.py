from ts3plugin import ts3plugin, PluginHost
import ts3, ts3defines, datetime, sqlite3, re


class channelWatcher(ts3plugin):
    name = "Channel Watcher"
    apiVersion = 20
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Helps you keeping your channel moderated.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = "cw"
    infoTitle = ""
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Channel Watcher", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Add to watched channels", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 1, "Remove from watched channels", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Check this client!", "")]
    hotkeys = []
    debug = False
    toggle = True
    autoBan = True
    autoMod = True
    autoCheckOnChannel = False
    requested = False
    #requestedUID = []
    requestedC = []
    banned = False
    banned_names = ["BAN", "NOT WELCOME"]
    mod_names = ["MOD", "OPERATOR"]
    admin_names = ["ADMIN"]
    sbgroup = 0
    smgroup = 0
    sagroup = 0
    ownchannels = []


    def __init__(self):
        ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/Bluscream]Bluscream[/url] loaded.")
        self.conn = sqlite3.connect(ts3.getConfigPath() + "settings.db")

    def InContacts(self, uid):
        c = self.conn.cursor()
        c.execute("SELECT value FROM contacts WHERE value LIKE '%IDS=" + uid + "%'")
        line = c.fetchone()
        if line is not None:
            line = line[0]
            isFriend = line.split("\n")[1]
            isFriend = isFriend.split("Friend=")[1]
            return int(isFriend)
        else:
            return -1

    def checkUser(self, uid):
        if self.toggle:
            if len(self.ownchannels) > 0:
                if uid != "serveradmin" and uid != "ServerQuery":
                    _in = self.InContacts(uid)
                    if _in != -1:
                        _schid = ts3.getCurrentServerConnectionHandlerID()
                        #self.requestedUID.extend([uid])
                        self.requestedC.extend([_in])
                        _dbid = ts3.requestClientDBIDfromUID(_schid, uid)

    def checkAllUsers(self):
        if self.toggle:
            _schid = ts3.getCurrentServerConnectionHandlerID()
            (error, _clid) = ts3.getClientID(_schid)
            (error, cl) = ts3.getClientList(_schid)
            for user in cl:
                if user != _clid:
                    (error, uid) = ts3.getClientVariableAsString(_schid, user, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                    self.checkUser(uid)

    def processCommand(self, schid, command):
        if command.startswith("test"):
            ts3.printMessageToCurrentTab("Status: "+str(self.toggle))
            ts3.printMessageToCurrentTab("Ban: "+str(self.sbgroup))
            ts3.printMessageToCurrentTab("Mod: "+str(self.smgroup))
            ts3.printMessageToCurrentTab("Admin: "+str(self.sagroup))
            ts3.printMessageToCurrentTab("Own Channels: "+str(self.ownchannels))
            #ts3.printMessageToCurrentTab("requestedUIDs: "+str(self.requestedUID))
            ts3.printMessageToCurrentTab("requestedCs: "+str(self.requestedC))
            return True
        if command.startswith("addchan"):
            command = int(command.split("addchan ")[1])
            self.ownchannels.extend([command])
            ts3.printMessageToCurrentTab("[color=green]Added[/color] #"+str(command)+" to list of channels: "+str(self.ownchannels))
            return True
        if command.startswith("delchan"):
            command = int(command.split("delchan ")[1])
            self.ownchannels.remove([command])
            ts3.printMessageToCurrentTab("[color=red]Removed[/color] #"+str(command)+" from list of channels: "+str(self.ownchannels))
            return True
        if command == "checkall":
            self.checkAllUsers()
            return True

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0:
                self.toggle = not self.toggle
                ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.datetime.now())+" Set Auto Channel Commander to [color=yellow]"+str(self.toggle)+"[/color]")
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL:
            if menuItemID == 0:
                self.ownchannels.extend([selectedItemID])
                ts3.printMessageToCurrentTab("[color=green]Added[/color] #"+str(selectedItemID)+" to list of channels: "+str(self.ownchannels))
            elif menuItemID == 1:
                self.ownchannels.remove(selectedItemID)
                ts3.printMessageToCurrentTab("[color=red]Removed[/color] #"+str(selectedItemID)+" from list of channels: "+str(self.ownchannels))
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            if menuItemID == 0:
                schid = ts3.getCurrentServerConnectionHandlerID()
                (error, uid) = ts3.getClientVariableAsString(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                _i = self.checkUser(uid)
                ts3.printMessageToCurrentTab("Client "+str(uid)+" = "+_i) # IMPORTANT

    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        if self.toggle:
            if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHING:
                self.requested = True
                ts3.requestChannelGroupList(ts3.getCurrentServerConnectionHandlerID())
            #elif newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
                self.ownchannels.clear()

    def onChannelGroupListEvent(self, serverConnectionHandlerID, channelGroupID, name, atype, iconID, saveDB):
        if self.toggle:
            if self.requested == True:
                for _name in self.banned_names:
                    if name.upper().__contains__(_name):
                        self.sbgroup = channelGroupID
                        break
                for _name in self.mod_names:
                    if name.upper().__contains__(_name):
                        self.smgroup = channelGroupID
                        break
                for _name in self.admin_names:
                    if name.upper().__contains__(_name):
                        self.sagroup = channelGroupID
                        break

    def onChannelGroupListFinishedEvent(self, serverConnectionHandlerID):
        if self.toggle:
            self.requested = False

    def onClientChannelGroupChangedEvent(self, serverConnectionHandlerID, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        if self.toggle:
            (error, _clid) = ts3.getClientID(serverConnectionHandlerID)
            if clientID == _clid:
                if channelGroupID == self.sagroup:
                    if self.ownchannels.__contains__(channelID):
                        _t = False
                    else:
                        self.ownchannels.append(channelID)

    def onClientMoveEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if self.toggle:
            (error, _clid) = ts3.getClientID(serverConnectionHandlerID)
            if clientID != _clid and oldChannelID == 0:
                schid = ts3.getCurrentServerConnectionHandlerID()
                (error, uid) = ts3.getClientVariableAsString(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                self.checkUser(uid)

    def onClientMoveSubscriptionEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility):
        if self.toggle:
            (error, _clid) = ts3.getClientID(serverConnectionHandlerID)
            if clientID != _clid:
                schid = ts3.getCurrentServerConnectionHandlerID()
                (error, uid) = ts3.getClientVariableAsString(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                self.checkUser(uid)

    def onNewChannelCreatedEvent(self, serverConnectionHandlerID, channelID, channelParentID, invokerID, invokerName, invokerUniqueIdentifier):
        if self.toggle and self.autoCheckOnChannel:
            (error, _clid) = ts3.getClientID(serverConnectionHandlerID)
            if invokerID == _clid:
                self.checkAllUsers()

    def onDelChannelEvent(self, serverConnectionHandlerID, channelID, invokerID, invokerName, invokerUniqueIdentifier):
        if self.toggle:
            if self.ownchannels.__contains__(channelID):
                self.ownchannels.remove(channelID)

    def onClientDBIDfromUIDEvent(self, serverConnectionHandlerID, uniqueClientIdentifier, clientDatabaseID):
        if self.toggle:
            #if self.requestedUID != "" and self.requestedUID[0] == uniqueClientIdentifier:
                _schid = ts3.getCurrentServerConnectionHandlerID()
                #_uid = self.requestedUID.pop(0)
                _cid = self.requestedC.pop(0)
                #_clid = ts3.requestClientIDs([_schid], uniqueClientIdentifier)
                #_cgid = ts3.getClientVariableAsInt(_schid, _clid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
                if _cid == 0 and self.autoMod:# and _cgid != self.smgroup
                    ts3.requestSetClientChannelGroup(_schid, [self.smgroup], self.ownchannels, [clientDatabaseID])
                    ts3.printMessageToCurrentTab("[color=green]Gave Client [URL=client://0/"+uniqueClientIdentifier+"]"+uniqueClientIdentifier+"[/URL] Channel Mod in #"+str(self.ownchannels)+"[/color]")
                elif _cid == 1 and self.autoBan:# and _cgid != self.sbgroup
                    ts3.requestSetClientChannelGroup(_schid, [self.sbgroup], self.ownchannels, [clientDatabaseID])
                    ts3.printMessageToCurrentTab("[color=red]Banned Client [URL=client://0/"+uniqueClientIdentifier+"]"+uniqueClientIdentifier+"[/URL] from Channels #"+str(self.ownchannels)+"[/color]")
