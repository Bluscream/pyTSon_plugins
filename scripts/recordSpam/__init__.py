import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from pytson import getCurrentApiVersion
from bluscream import timestamp, sendCommand, getAddons, inputInt, calculateInterval, AntiFloodPoints, escapeStr

class recordSpam(ts3plugin):
    name = "Record Spam"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "( .) ( .)"
    offersConfigure = False
    commandKeyword = "rec"
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "scripts/%s/record.svg"%__name__)]
    hotkeys = [
        ("request_talk_power", "Request Talk Power")
    ]
    timer = QTimer()
    hook = False
    schid = 0
    tpr_name = "Talk Power bitte?"

    def __init__(self):
        addons = getAddons()
        for k in addons:
            if addons[k]["name"] == "TS3Hook": self.hook = True; break
        self.timer.timeout.connect(self.tick)
        self.timer.setTimerType(2)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self): self.timer.stop()

    def processCommand(self, schid, keyword): self.onHotkeyOrCommandEvent(keyword, schid)
    def onHotkeyEvent(self, keyword): self.onHotkeyOrCommandEvent(keyword)
    def onHotkeyOrCommandEvent(self, keyword, schid=0):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        if keyword == "request_talk_power":
            (err, oldnick) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
            ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, self.tpr_name)
            ts3lib.flushClientSelfUpdates(schid)
            if self.hook:
                sendCommand(self.name, "clientupdate client_is_recording=1", schid)
                sendCommand(self.name, "clientupdate client_is_recording=0", schid)
            else:
                ts3lib.startVoiceRecording(schid)
                ts3lib.stopVoiceRecording(schid)
            ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, oldnick)
            ts3lib.flushClientSelfUpdates(schid)

    def onServerUpdatedEvent(self, schid):
        if not self.schid == schid: return
        self.timer.start(calculateInterval(schid, AntiFloodPoints.CLIENTUPDATE*2, self.name))

    def startVoiceRecording(self, schid):
        if self.hook: sendCommand(self.name, "clientupdate client_is_recording=1", schid)
        else:
            # ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientProperties.CLIENT_IS_RECORDING, True)
            ts3lib.startVoiceRecording(schid)
    def stopVoiceRecording(self, schid):
        if self.hook: sendCommand(self.name, "clientupdate client_is_recording=0", schid)
        else:
            # ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientProperties.CLIENT_IS_RECORDING, False)
            ts3lib.stopVoiceRecording(schid)

    def tick(self):
        schid = self.schid
        if not schid or schid < 1: self.timer.stop()
        # self.startVoiceRecording(self.schid)
        # self.stopVoiceRecording(self.schid)
        if self.hook:
            sendCommand(self.name, "clientupdate client_is_recording=1", schid)
            sendCommand(self.name, "clientupdate client_is_recording=0", schid)
        else:
            ts3lib.startVoiceRecording(schid)
            ts3lib.stopVoiceRecording(schid)

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

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if not self.timer.isActive(): return
        if error == ts3defines.ERROR_client_is_flooding:
            ts3lib.printMessageToCurrentTab("{}: [color=red][b]Client is flooding, stopping!".format(self.name))
            self.timer.stop()
            if self.hook: sendCommand(self.name, "clientupdate client_is_recording=0", self.schid)
            else: ts3lib.stopVoiceRecording(self.schid)
            return True

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_DISCONNECTED: return
        if schid != self.schid: return
        self.timer.stop()
        self.schid = 0