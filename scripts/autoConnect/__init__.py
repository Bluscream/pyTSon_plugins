import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp

class autoConnect(ts3plugin):
    name = "Auto Connect"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "connect"
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, "scripts/%s/connect.svg"%__name__)]
    hotkeys = [("connect", name)]

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))


    def menuCreated(self): self.checkServer()
    def currentServerConnectionChanged(self, schid):self.checkServer(schid)
    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        self.checkServer(schid, newStatus)
    def checkServer(self, schid=0, status=None):
        if schid < 1: schid = ts3lib.getCurrentServerConnectionHandlerID()
        if status is None: (err, status) = ts3lib.getConnectionStatus(schid)
        if status == ts3defines.ConnectStatus.STATUS_DISCONNECTED: status = True
        elif status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: status = False
        else: return
        for menuItem in self.menuItems:
            try: ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, menuItem[1]), status)
            except: pass

    def onMenuItemEvent(self, schid, atype, mID, selectedItemID): self.connect()
    def processCommand(self, schid, keyword): self.connect()
    def onHotkeyEvent(self, keyword): self.connect()

    def connect(self):
        (err, schid) = ts3lib.spawnNewServerConnectionHandler(1337)
        ts3lib.startConnection(schid, "", "51.255.133.6", 9987, "Bluscream from 127.0.0.1:1337", [], "123", "123")