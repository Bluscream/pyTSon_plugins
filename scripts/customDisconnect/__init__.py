import ts3lib, ts3defines
from ts3defines import ConnectStatus
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from PythonQt.Qt import QApplication
from bluscream import timestamp, sendCommand, inputBox

class customDisconnect(ts3plugin):
    name = "Custom Disconnect"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "disconnect"
    infoTitle = None
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Disconnect", "scripts/%s/disconnect.svg"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Close Tab", "scripts/%s/tab_close_button.svg"%__name__)
    ]
    hotkeys = [
        ("disconnect", "Prompts for disconnect message before disconnecting"),
        ("close_tab", "Prompts for disconnect message before closing the current tab")
    ]

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, mID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL: return
        self.disconnect(schid, True if mID == 1 else False)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber): self.checkServer(schid, newStatus)
    def currentServerConnectionChanged(self, schid): self.checkServer(schid, ts3lib.getConnectionStatus(schid))
    def checkServer(self, schid, status):
        if status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: status = True
        elif status == ts3defines.ConnectStatus.STATUS_DISCONNECTED: status = False
        else: return
        for menuItem in self.menuItems:
            try: ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, menuItem[1]), status)
            except: pass


    def processCommand(self, schid, keyword): self.onHotkeyOrCommandEvent(keyword, schid)
    def onHotkeyEvent(self, keyword): self.onHotkeyOrCommandEvent(keyword)
    def onHotkeyOrCommandEvent(self, keyword, schid=0):
        if keyword == "disconnect": self.disconnect(schid)
        elif keyword == "close_tab": self.disconnect(schid, True)

    def disconnect(self, schid=0, close_tab=False):
        if schid < 1: schid = ts3lib.getCurrentServerConnectionHandlerID()
        status = ts3lib.getConnectionStatus(schid)
        if status != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        clipboard = QApplication.clipboard().text()
        msg = inputBox("Disconnect", "Message", clipboard)
        ts3lib.stopConnection(schid, msg if msg else "")
        if close_tab: ts3lib.destroyServerConnectionHandler(schid)