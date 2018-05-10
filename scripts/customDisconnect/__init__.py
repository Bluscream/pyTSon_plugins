import ts3lib, ts3defines
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
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Disconnect", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Close Tab", "")
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

    def processCommand(self, schid, keyword): self.onHotkeyOrCommandEvent(keyword, schid)

    def onHotkeyEvent(self, keyword): self.onHotkeyOrCommandEvent(keyword)

    def onHotkeyOrCommandEvent(self, keyword, schid=0):
        if keyword == "disconnect": self.disconnect(schid)
        elif keyword == "close_tab": self.disconnect(schid, True)

    def disconnect(self, schid=0, close_tab=False):
        if schid < 1: schid = ts3lib.getCurrentServerConnectionHandlerID()
        clipboard = QApplication.clipboard().text()
        msg = inputBox("Disconnect", "Message", clipboard)
        ts3lib.stopConnection(schid, msg if msg else "")
        if close_tab: ts3lib.destroyServerConnectionHandler(schid)