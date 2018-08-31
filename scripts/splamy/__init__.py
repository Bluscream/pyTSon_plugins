import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from bluscream import timestamp

class splamy(ts3plugin):
    name = "splamy"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = []
    suid = "Izjl13xjEt0LN8mlAWlvHNeKn1w="
    cluid = "uA0U7t4PBxdJ5TLnarsOHQh4/tY="
    returnCode = ""

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        ts3lib.requestClientIDs(schid,self.cluid)

    def onClientIDsEvent(self, schid, uniqueClientIdentifier, clientID, clientName):
        if not self.cluid  == uniqueClientIdentifier: return
        ts3lib.requestSendPrivateTextMsg(schid, "Hallo %s"%clientName, clientID)
        self.returnCode = ""