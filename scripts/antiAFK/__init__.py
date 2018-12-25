import ts3lib, ts3defines
from random import randint
from datetime import datetime
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from pytson import getCurrentApiVersion
from bluscream import timestamp, sendCommand, getAddons, getScriptPath

class antiAFK(ts3plugin):
    path = getScriptPath(__name__)
    name = "Anti AFK"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Never get moved by being AFK again."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    timer = QTimer()
    servers = {}
    text = "." #~cmdclientupdate
    interval = {
        "9Sx6wrlRV4i9klBiTanrksNFKvs=": (5, 10),
        "QTRtPmYiSKpMS8Oyd4hyztcvLqU=": (30, 120),
        "default": (10, 30)
    }
    retcode = ""
    hook = False

    def __init__(self):
        addons = getAddons()
        for k in addons:
            if addons[k]["name"] == "TS3Hook": self.hook = True; break
        self.timer.timeout.connect(self.tick)
        self.timer.setTimerType(2)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        for schid in self.servers:
            self.delTimer(schid)

    def addTimer(self, schid):
        err, clid = ts3lib.getClientID(schid)
        self.servers[schid] = {"clid": clid}
        interval = self.getInterval(schid)
        if len(self.servers) == 1:
            self.timer.start(interval["interval"])
        ts3lib.printMessageToCurrentTab("{}> Enabled for tab #{} with interval {} (server uid: {})".format(self.name, schid, interval["interval"], interval["suid"]))

    def getInterval(self, schid=0):
        if schid < 1: schid = ts3lib.getCurrentServerConnectionHandlerID()
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if not suid in self.interval: suid = "default"
        min = self.interval[suid][0]*1000
        max = self.interval[suid][1] * 1000
        _return = { "schid": schid, "suid": suid, "min": min, "max": max, "interval": randint(min, max) }
        if PluginHost.cfg.getboolean("general", "verbose"): print(_return)
        return _return

    def delTimer(self, schid):
        if schid in self.servers:
            # print(self.name, "> Removing Timer:", self.servers[schid], "for #", schid, "(servers:", len(self.servers)-1,")")
            del self.servers[schid]
            if len(self.servers) == 0: self.timer.stop()
            ts3lib.printMessageToCurrentTab("{}> Disabled for tab #{}".format(self.name, schid))

    def tick(self):
        for schid in self.servers:
            if self.hook: sendCommand(self.name, "clientupdate", schid)
            else:
                self.retcode = ts3lib.createReturnCode()
                ts3lib.requestSendPrivateTextMsg(schid, self.text, self.servers[schid]["clid"], self.retcode)
            interval = self.getInterval()
            # print(self.name, ">", "Sent", self.text, "for schid", schid, "to clid", self.servers[schid]["clid"], "| new interval:", interval)
            self.timer.setInterval(interval)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        if schid in self.servers: self.delTimer(schid)
        else: self.addTimer(schid)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED: self.delTimer(schid)

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if schid in self.servers and fromID == self.servers[schid]["clid"] and targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT and message == self.text: return 1

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode == self.retcode: return True

    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        if returnCode == self.retcode: return True