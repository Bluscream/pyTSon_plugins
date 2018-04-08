from os import path
import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from pytson import getPluginPath, getCurrentApiVersion
from bluscream import timestamp
from random import choice

class nameSwitcher(ts3plugin):
    name = "Name Switcher"
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
    timer = QTimer()
    interval = 1 * 1000 * 60
    prefix = "Danny"
    suffixes = path.join(getPluginPath(), "scripts", "nameSwitcher", "suffixes.txt")
    last = ""
    schid = 0
    retcode = ""

    def __init__(self):
        self.timer.timeout.connect(self.tick)
        self.timer.setTimerType(2)
        with open(self.suffixes) as f:
            self.suffixes = f.read().splitlines()
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        if self.timer.isActive(): self.timer.stop()

    def tick(self):
        new = choice(self.suffixes)
        while new == self.last: new = choice(self.suffixes)
        ts3lib.setClientSelfVariableAsString(self.schid, ts3defines.ClientProperties.CLIENT_NICKNAME, self.prefix + new)
        self.retcode = ts3lib.createReturnCode()
        ts3lib.flushClientSelfUpdates(self.schid, self.retcode)
        self.last = new

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        if self.timer.isActive(): self.timer.stop()
        else:
            self.schid = schid
            self.timer.start(self.interval)
            self.tick()

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if self.timer.isActive(): self.timer.stop()

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode != self.retcode: return
        self.retcode = ""
        if error == ts3defines.ERROR_client_nickname_inuse: self.tick()
        return True
