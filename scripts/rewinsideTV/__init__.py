import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from datetime import datetime
from bluscream import timestamp, intList

class rewinsideTV(ts3plugin):
    name = "Rewi nifty tricks"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = []
    suid = "9Sx6wrlRV4i9klBiTanrksNFKvs="
    waiting = []
    mychan = 0
    sgid_guest = 10
    cgid_guest = 10
    cgid_mod = 14
    cgid_admin = 9

    def __init__(self):
        # schid = ts3lib.getCurrentServerConnectionHandlerID()
        # err, clid = ts3lib.getClientID(schid)
        # err, self.mychan = ts3lib.getChannelOfClient(schid, clid)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        (err, self.sgid_guest) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_SERVER_GROUP)
        (err, self.cgid_guest) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
        (err, self.cgid_admin) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_ADMIN_GROUP)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if self.mychan == 0: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID == ownID: return
        if clientID and (newChannelID == 0 or newChannelID == self.mychan):
            if newChannelID == self.mychan:
                (err, dbid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Removing {} from self.waiting".format(clientID))
            ts3lib.requestSetClientChannelGroup(schid, [self.sgid_guest], [self.mychan], [self.waiting[clientID]])
            self.waiting.remove(dbid)
            return
        if newChannelID == 0: return
        if oldChannelID != 0: return
        (err, sgids) = ts3lib.getClientVariableAsString(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        if self.sgid_guest in intList(sgids):
            (err, dbid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
            self.waiting.append(dbid)
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("#{} Found new guest {} ({}) giving him channel mod until he's here ;)".format(schid, clientID, dbid))
            ts3lib.requestSetClientChannelGroup(schid, [14], [self.mychan], [dbid])
            return

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID == ownID:
            if channelGroupID == self.cgid_admin: self.mychan = channelID
            else: self.mychan = 0
            return
