import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp

class teaspeak(ts3plugin):
    name = "TeaSpeak"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "TeaSpeak implementation"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "List Musicbots", "scripts/%s/teaspeak.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "List Musicbots", "scripts/%s/teaspeak.png"%__name__)
    ]
    hotkeys = []

    def __init__(self):
        ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def menuCreated(self): self.checkMenus()
    def currentServerConnectionChanged(self, schid): self.checkMenus(schid)
    def checkMenus(self, schid=0):
        if not self.name in PluginHost.active: return
        if schid < 1: schid = ts3lib.getCurrentServerConnectionHandlerID()
        err, status = ts3lib.getConnectionStatus(schid)
        if status != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: self.toggleMenus(False)
        else: self.toggleMenus(True)

    def toggleMenus(self, enabled):
        for menuItem in self.menuItems:
            try: ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, menuItem[1]), enabled)
            except: pass