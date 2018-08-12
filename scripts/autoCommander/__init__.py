import ts3defines, ts3lib
from enum import Enum
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import Qt, QTimer
from bluscream import timestamp, inputInt, calculateInterval, AntiFloodPoints

class autoCommanderMode(Enum):
    OFF = 0
    CHANNELGROUP_ASSIGNED = 1
    START_TALKING = 2

class autoCommander(ts3plugin):
    name = "Auto Channel Commander"
    apiVersion = 22
    requestAutoload = False
    version = "1.1"
    author = "Bluscream"
    description = "Automatically enable channel commander when switching channels.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle %s"%name, "scripts/%s/commander_off.svg"%__name__),
        # (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Toggle Commander while talking", "scripts/%s/commander_off.svg"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Toggle Channel Commander Spam", "scripts/%s/commander.svg"%__name__)
    ]
    hotkeys = []
    timer = QTimer()
    schid = 0
    requested = 0
    mode = autoCommanderMode.OFF
    retcode = ""

    def __init__(self):
        self.timer.timeout.connect(self.tick)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def stop(self):
        if self.timer.isActive(): self.timer.stop()

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
        if not self.mode: return
        if self.requested != schid: return
        self.requested = 0
        self.schid = schid
        self.timer.start(calculateInterval(schid, AntiFloodPoints.CLIENTUPDATE, self.name))

    def setChannelCommander(self, schid, enabled):
        ts3lib.setClientSelfVariableAsInt(schid, ts3lib.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, enabled)
        self.retcode = ts3lib.createReturnCode()
        ts3lib.flushClientSelfUpdates(schid, self.retcode)

    def tick(self):
        (err, commander) =ts3lib.getClientSelfVariable(self.schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER)
        self.setChannelCommander(self.schid, not commander)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            if self.mode == autoCommanderMode.OFF:
                self.mode = autoCommanderMode.CHANNELGROUP_ASSIGNED
            elif self.mode == autoCommanderMode.CHANNELGROUP_ASSIGNED:
                self.mode = autoCommanderMode.START_TALKING
            else: self.mode = autoCommanderMode.OFF
        elif menuItemID == 1: self.toggleTimer(schid); return
        ts3lib.printMessageToCurrentTab("{} > Switched mode to: [color=orange]{}".format(self.name, self.mode.name))

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        if not self.mode == autoCommanderMode.CHANNELGROUP_ASSIGNED: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID: return
        (err, val) = ts3lib.getClientNeededPermission(schid, "b_client_use_channel_commander")
        if val: return
        ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
        ts3lib.flushClientSelfUpdates(schid, self.retcode)

    def onTalkStatusChangeEvent(self, schid, status, isReceivedWhisper, clid):
        if not self.mode == autoCommanderMode.START_TALKING: return
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID != clid: return
        (err, commander) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER)
        if status == ts3defines.TalkStatus.STATUS_TALKING and not commander: self.setChannelCommander(schid, True)
        elif status == ts3defines.TalkStatus.STATUS_NOT_TALKING and commander: self.setChannelCommander(schid, False)

    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        if returnCode != self.retcode: return
        return True

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode != self.retcode: return
        if error == ts3defines.ERROR_client_is_flooding:
            ts3lib.printMessageToCurrentTab("{}: [color=red][b]Client is flooding, stopping!".format(self.name))
            self.timer.stop()
        return True