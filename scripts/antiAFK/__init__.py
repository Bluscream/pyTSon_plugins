import ts3lib, ts3defines
from random import randint
from datetime import datetime
from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer
from bluscream import timestamp, sendCommand

class antiAFK(ts3plugin):
    name = "Anti AFK"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Never get moved by being AFK again."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    debug = False
    timers = {}
    text = "."
    ts3hook = True
    interval = randint(30*1000,120*1000)

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        for schid, timer in self.timers.items():
            self.stopTimer(schid)

    def startTimer(self, schid):
        err, clid = ts3lib.getClientID(schid)
        self.timers[schid] = {"timer": QTimer(), "clid": clid}
        if self.ts3hook: self.timers[schid]["timer"].timeout.connect(self.tickhook)
        else: self.timers[schid]["timer"].timeout.connect(self.tick)
        self.timers[schid]["timer"].start(self.interval)

    def stopTimer(self, schid):
        if schid in self.timers:
            self.timers[schid]["timer"].stop()
            del self.timers[schid]

    def tickhook(self): sendCommand(self.name, "clientupdate")

    def tick(self):
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        ts3lib.requestSendPrivateTextMsg(schid, self.text, self.timers[schid]["clid"], "antiAFK:auto")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        if schid in self.timers: self.stopTimer(schid)
        else: self.startTimer(schid)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED: self.stopTimer(schid)

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if not self.ts3hook and fromID == self.timers[schid]["clid"] and targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT and message == self.text: return 1

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode == "antiAFK:auto": return True
