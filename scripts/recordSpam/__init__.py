import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from pytson import getCurrentApiVersion
from bluscream import timestamp, sendCommand, getAddons, inputInt, calculateInterval, AntiFloodPoints

class recordSpam(ts3plugin):
    name = "Record Spam"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "( .) ( .)"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    timer = QTimer()
    hook = False
    schid = 0

    def __init__(self):
        addons = getAddons()
        for k in addons:
            if addons[k]["name"] == "TS3Hook": self.hook = True; break
        self.timer.timeout.connect(self.tick)
        self.timer.setTimerType(2)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self): self.timer.stop()

    def onServerUpdatedEvent(self, schid):
        if not self.schid == schid: return
        self.timer.start(calculateInterval(schid, AntiFloodPoints.CLIENTUPDATE*2, self.name))

    def tick(self):
        if not self.schid or self.schid < 1: self.timer.stop()
        if self.hook:
            sendCommand(self.name, "clientupdate client_is_recording=1", self.schid)
            sendCommand(self.name, "clientupdate client_is_recording=0", self.schid)
        else:
            ts3lib.startVoiceRecording(self.schid)
            ts3lib.stopVoiceRecording(self.schid)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        if self.timer.isActive():
            self.timer.stop()
            self.schid = 0
        else:
            interval = inputInt(self.name, 'Interval in Milliseconds:')
            self.schid = schid
            if interval < 1: ts3lib.requestServerVariables(schid)
            else: self.timer.start(interval)


    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_DISCONNECTED: return
        if schid != self.schid: return
        self.timer.stop()
        self.schid = 0