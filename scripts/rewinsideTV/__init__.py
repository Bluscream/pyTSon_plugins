import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from datetime import datetime
from bluscream import timestamp, intList, clientURL, getContactStatus, ContactStatus

class rewinsideTV(ts3plugin):
    name = "Rewi nifty tricks"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "rewi"
    infoTitle = None
    hotkeys = [("rewi_toggle", "Toggles the rewinside script")]
    menuItems = []
    suid = "9Sx6wrlRV4i9klBiTanrksNFKvs="
    enabled = True
    waiting = {}
    mychan = 0
    sgid_guest = 10
    cgid_guest = 10
    cgid_mod = 14
    cgid_admin = 9
    schid = 0

    def __init__(self):
        if self.enabled:
            schid = ts3lib.getCurrentServerConnectionHandlerID()
            (err,status) = ts3lib.getConnectionStatus(schid)
            if status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
                err, clid = ts3lib.getClientID(schid)
                err, self.mychan = ts3lib.getChannelOfClient(schid, clid)
                self.schid = schid
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def processCommand(self, schid, keyword): return self.onHotkeyOrCommandEvent(keyword)
    def onHotkeyEvent(self, keyword): self.onHotkeyOrCommandEvent(keyword.replace("rewi_",""))
    def onHotkeyOrCommandEvent(self, keyword):
        if keyword == "toggle":
            self.enabled = not self.enabled
            ts3lib.printMessageToCurrentTab("Set {} to {}".format(self.name, self.enabled))
            return True

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if not self.enabled: return
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        (err, self.sgid_guest) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_SERVER_GROUP)
        (err, self.cgid_guest) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
        (err, self.cgid_admin) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_ADMIN_GROUP)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.enabled: return
        if self.schid != schid: return
        if not self.mychan: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID == ownID: return
        if clientID in self.waiting and (newChannelID == 0 or newChannelID == self.mychan):
            # if newChannelID == self.mychan:
                # (err, dbid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
            ts3lib.printMessage(schid, "{}: [color=orange]Removing channel mod from {}".format(self.name, self.waiting[clientID] if newChannelID == 0 else clientURL(schid, clientID)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
            ts3lib.requestSetClientChannelGroup(schid, [self.sgid_guest], [self.mychan], [self.waiting[clientID]])
            del self.waiting[clientID]
            return
        if newChannelID == 0 or oldChannelID != 0: return
        (err, sgids) = ts3lib.getClientVariableAsString(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        if not self.sgid_guest in intList(sgids): return
        # TODO Any way to get the cgid in another channel?
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if getContactStatus(uid) == ContactStatus.BLOCKED:
            ts3lib.printMessage(schid, "{}: [color=red]Not allowing blocked user {} in your channel.".format(self.name, clientURL(schid, clientID)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
            return
        (err, dbid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        self.waiting[clientID] = dbid
        ts3lib.printMessage(schid, "{}:  [color=green]Found new guest {} giving him channel mod until he's here ;)".format(self.name, clientURL(schid, clientID)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
        ts3lib.requestSetClientChannelGroup(schid, [self.cgid_mod], [self.mychan], [dbid])

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        if not self.enabled: return
        if self.schid != schid: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID == ownID:
            if channelGroupID == self.cgid_admin:
                self.schid = schid
                self.mychan = channelID
            else: self.mychan = 0
            return
