import ts3lib, ts3defines
from random import randint
from datetime import datetime
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from pytson import getCurrentApiVersion
from bluscream import timestamp, sendCommand, getAddons

class troll(ts3plugin):
    name = "Troll"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    enabled = False
    retcode = ""

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return

    def onServerGroupClientAddedEvent(self, serverConnectionHandlerID, clientID, clientName, clientUniqueIdentity, serverGroupID, invokerClientID, invokerName, invokerUniqueIdentity):
        pass

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode == self.retcode: self.retcode = ""; return True
