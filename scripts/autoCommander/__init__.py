import ts3defines, ts3lib
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import Qt, QTimer
from bluscream import timestamp, inputInt, calculateInterval, AntiFloodPoints, escapeStr

class autoCommander(ts3plugin):
    name = "Auto Channel Commander"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Automatically enable channel commander when switching channels.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle %s"%name, "scripts/%s/commander_off.svg"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Toggle Channel Commander Spam", "scripts/%s/commander.svg"%__name__)
    ]
    hotkeys = []
    timer = QTimer()
    schid = 0
    requested = 0
    retcode = __name__
    enabled = False

    def __init__(self):
        self.timer.timeout.connect(self.tick)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def stop(self):
        if self.timer.isActive(): self.timer.stop()
        del self.timer

    def toggleTimer(self, schid):
        if self.timer.isActive():
            self.timer.stop()
        else:
            interval = inputInt(self.name, 'Interval in Milliseconds:')
            self.schid = schid
            if interval < 1:
                self.requested = schid
                ts3lib.requestServerVariables(schid)
            else: self.timer.start(interval)

    def onServerUpdatedEvent(self, schid):
        if not self.enabled: return
        if self.requested != schid: return
        self.requested = 0
        self.schid = schid
        self.timer.start(calculateInterval(schid, AntiFloodPoints.CLIENTUPDATE, self.name))

    def tick(self):
        (err, commander) =ts3lib.getClientSelfVariable(self.schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER)
        ts3lib.setClientSelfVariableAsInt(self.schid, ts3lib.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, not commander)
        ts3lib.flushClientSelfUpdates(self.schid, self.retcode)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0: self.enabled = not self.enabled
        elif menuItemID == 1: self.toggleTimer(schid)

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        if not self.enabled: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID: return
        (err, val) = ts3lib.getClientNeededPermission(schid, "b_client_use_channel_commander")
        if val: return
        ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
        ts3lib.flushClientSelfUpdates(schid, self.retcode)

    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        if not self.enabled: return
        print(self.name, "returnCode", returnCode, "self.retcode", self.retcode)
        if returnCode != self.retcode: return
        # if failedPermissionID == 185: return True
        return True

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if not self.enabled: return
        print(self.name, "returnCode", returnCode, "self.retcode", self.retcode)
        if returnCode != self.retcode: return
        print("test")
        if error == ts3defines.ERROR_client_is_flooding:
            ts3lib.printMessageToCurrentTab("{}: [color=red][b]Client is flooding, stopping!".format(self.name))
            self.timer.stop()
            return True
        elif error == ts3defines.ERROR_ok:
            return True