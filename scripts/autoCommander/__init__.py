import ts3defines, ts3lib
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import Qt, QTimer
from bluscream import timestamp, inputInt, calculateInterval, AntiFloodPoints

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
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Channel Commander Spam", "")
    ]
    hotkeys = []
    timer = None
    schid = 0

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def toggleTimer(self, schid):
        if self.timer is None:
            self.timer = QTimer()
            self.timer.timeout.connect(self.tick)
        if self.timer.isActive():
            self.timer.stop()
            self.timer = None
        else:
            interval = inputInt(self.name, 'Interval in Milliseconds:')
            self.schid = schid
            if interval < 1: ts3lib.requestServerVariables(schid)
            else: self.timer.start(interval)

    def onServerUpdatedEvent(self, schid):
        if not self.schid == schid: return
        self.timer.start(calculateInterval(schid, AntiFloodPoints.CLIENTUPDATE, self.name))

    def tick(self):
        (err, commander) =ts3lib.getClientSelfVariable(self.schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER)
        ts3lib.setClientSelfVariableAsInt(self.schid, ts3lib.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, not commander)
        ts3lib.flushClientSelfUpdates(self.schid)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0: self.toggleTimer(schid)

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID: return
        (err, val) = ts3lib.getClientNeededPermission(schid, "b_client_use_channel_commander")
        if val: return
        ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
        ts3lib.flushClientSelfUpdates(schid)

    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        if failedPermissionID == 185: return True