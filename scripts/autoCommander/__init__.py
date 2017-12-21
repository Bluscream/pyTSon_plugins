import ts3defines, ts3lib
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtGui import QInputDialog, QWidget
from PythonQt.QtCore import Qt, QTimer

def inputBox(title, text):
    x = QWidget()
    x.setAttribute(Qt.WA_DeleteOnClose)
    return QInputDialog.getText(x, title, text)

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
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Auto Channel Commander", ""), (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Toggle Channel Commander Spam", "")]
    hotkeys = []
    debug = False
    toggle = False
    timer = None
    schid = 0
    current = False
    requested = False
    mod_names = ["ADMIN", "MOD", "OPERATOR"]
    smgroup = []

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def toggleTimer(self, schid):
            if self.timer is None:
                self.timer = QTimer()
                self.timer.timeout.connect(self.tick)
            if self.timer.isActive():
                self.timer.stop()
                self.timer = None
                ts3lib.printMessageToCurrentTab('Timer stopped!')
            else:
                step = inputBox(self.name, 'Interval in Milliseconds:')
                if step: interval = int(step)
                else: interval = 1000
                self.schid = schid
                self.timer.start(interval)
                ts3lib.printMessageToCurrentTab('Timer started!')

    def tick(self):
        self.current = not self.current
        ts3lib.setClientSelfVariableAsInt(self.schid, ts3lib.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, self.current)
        ts3lib.flushClientSelfUpdates(self.schid)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.toggle = not self.toggle
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.toggle))
        elif menuItemID == 1: self.toggleTimer(schid)

    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        if not self.toggle: return
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHING:
            self.requested = True
            ts3lib.requestChannelGroupList(ts3lib.getCurrentServerConnectionHandlerID())

    def onChannelGroupListEvent(self, serverConnectionHandlerID, channelGroupID, name, atype, iconID, saveDB):
        if not self.toggle: return
        if self.requested == True:
            for _name in self.mod_names:
                if name.upper().__contains__(_name):
                    self.smgroup.extend([channelGroupID])

    def onChannelGroupListFinishedEvent(self, serverConnectionHandlerID):
        if self.toggle: self.requested = False

    # def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
         #if not self.toggle: return
#         (error, cID) = ts3lib.getClientID(schid)
#         if error == ts3defines.ERROR_ok:
#             if cID == clientID:
#                 ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
#                 ts3lib.flushClientSelfUpdates(schid)
    #
    # def onClientMoveMovedEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
    #     if not self.toggle: return
#         (error, cID) = ts3lib.getClientID(schid)
#         if error == ts3defines.ERROR_ok:
#             if cID == clientID:
#                 ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
#                 ts3lib.flushClientSelfUpdates(schid)

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        if not self.toggle: return
        (error, cID) = ts3lib.getClientID(schid)
        if error == ts3defines.ERROR_ok:
            if cID == clientID:
                (error, cgID) = ts3lib.getClientVariableAsInt(schid, cID, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
                for _group in self.smgroup:
                    if cgID == _group:
                        ts3lib.setClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER, 1)
                        ts3lib.flushClientSelfUpdates(schid)
                        break
