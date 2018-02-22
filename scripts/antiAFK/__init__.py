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
    timer = QTimer()
    servers = {}
    text = "."
    interval = (10, 30)

    def __init__(self):
        addons = getAddons()
        hook = False
        for k in addons:
            if hasattr(k, "name") and k["name"] == "TS3Hook": hook = True; break
        if hook: self.timer.timeout.connect(self.tickhook)
        else: self.timer.timeout.connect(self.tick)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        for schid in self.servers:
            self.delTimer(schid)

    def addTimer(self, schid):
        err, clid = ts3lib.getClientID(schid)
        self.servers[schid] = {"clid": clid}
        self.servers[schid]["timer"].setTimerType(2)
        if len(self.servers) == 1: self.timer.start(randint(self.interval[0]*1000, self.interval[1]*1000))

    def delTimer(self, schid):
        if schid in self.servers:
            del self.servers[schid]
        if len(self.servers) == 0: self.timer.stop()

    def tickhook(self):
        for schid in self.servers:
            sendCommand(self.name, "clientupdate", schid)

    def tick(self):
        for schid in self.servers:
            ts3lib.requestSendPrivateTextMsg(schid, self.text, self.servers[schid]["clid"], "antiAFK:auto")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        if schid in self.servers: self.delTimer(schid)
        else: self.addTimer(schid)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED: self.delTimer(schid)

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if fromID == self.servers[schid]["clid"] and targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT and message == self.text: return 1

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode == "antiAFK:auto": return True
