import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp

class autoConnect(ts3plugin):
    name = "Auto Connect"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "connect"
    infoTitle = None
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, "scripts/%s/connect.svg"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Auto Disconnect", "scripts/%s/disconnect.svg"%__name__)
    ]
    hotkeys = [("connect", name)]
    schid = 0

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        if self.schid > 0: self.disconnect()

    def menuCreated(self): self.checkServer()
    def currentServerConnectionChanged(self, schid):self.checkServer()
    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        """if schid == self.schid:
            ts3lib.destroyServerConnectionHandler(schid)
            self.schid = 0
        else:"""
        self.checkServer()
    def checkServer(self):
        if self.schid > 0: (err, status) = ts3lib.getConnectionStatus(self.schid)
        else: status = ts3defines.ConnectStatus.STATUS_DISCONNECTED
        try:
            if status == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
                ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, self.menuItems[0][1]), True)
                ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, self.menuItems[1][1]), False)
            elif status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
                ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, self.menuItems[0][1]), False)
                ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, self.menuItems[1][1]), True)
        except: pass

    def onMenuItemEvent(self, schid, atype, mID, selectedItemID):
        if mID == 0: self.connect()
        elif mID == 1: self.disconnect()
    def processCommand(self, schid, keyword): self.connect()
    def onHotkeyEvent(self, keyword): self.connect()

    def connect(self):
        (err, schid) = ts3lib.spawnNewServerConnectionHandler(1337)
        print("err:",err,"schid:",schid)
        ts3lib.startConnection(schid, "", "51.255.133.6", 9987, "Bluscream from 127.0.0.1:1337", ["test"], "123", "123")
        return True

    def disconnect(self, schid=schid):
        (err, status) = ts3lib.getConnectionStatus(schid)
        if status != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        ts3lib.stopConnection(schid, "ts3lib.stopConnection({})".format(schid))
        ts3lib.destroyServerConnectionHandler(schid)