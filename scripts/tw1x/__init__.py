import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from bluscream import timestamp

class tw1x(ts3plugin):
    name = "tw1x"
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
    suid = "bJQTB/k5F16F6iX6jAL6mGZDy9c="
    sgid_nopoke = 19
    requested = ""

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        (err, uid) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        self.requested = uid
        ts3lib.requestClientDBIDfromUID(schid, uid)

    def onClientDBIDfromUIDEvent(self, schid, uniqueClientIdentifier, cldbid):
        if not self.requested  == uniqueClientIdentifier or not cldbid: return
        ts3lib.requestServerGroupAddClient(schid, self.sgid_nopoke, cldbid)
        self.requested = ""