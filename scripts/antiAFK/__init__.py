import ts3lib, ts3defines, traceback
from datetime import datetime
from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer


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
    enabled = False
    debug = True
    delay = 5000
    timer = None
    schid = 0
    clid = 0
    text = "."

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            if self.timer == None:
                self.timer = QTimer()
                self.timer.timeout.connect(self.tick)
            if self.timer.isActive():
                self.enabled = False
                self.timer.stop()
                self.timer = None
                self.schid = 0
                ts3lib.printMessageToCurrentTab('Timer stopped!')
            else:
                self.schid = schid
                self.clid = ts3lib.getClientID(schid)
                self.enabled = True
                self.timer.start(self.delay)
                ts3lib.printMessageToCurrentTab('Timer started!')

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if fromID == self.clid and targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT and message == self.text: return 1

    def tick(self):
        try:
            if not self.enabled: return
            ts3lib.requestSendPrivateTextMsg(self.schid, self.text, self.clid)
            # ts3lib.setClientSelfVariableAsInt(self.schid, ts3defines.ClientProperties.CLIENT_INPUT_MUTED, 1)
            # err = (ts3lib.flushClientSelfUpdates(self.schid))
            # ts3lib.setClientSelfVariableAsInt(self.schid, ts3defines.ClientProperties.CLIENT_INPUT_MUTED, 0)
            # err = (ts3lib.flushClientSelfUpdates(self.schid))
            # (err, smth) = ts3lib.requestClientIDs(self.schid, "e3dvocUFTE1UWIvtW8qzulnWErI=")
            # err = ts3lib.requestClientDBIDfromUID(self.schid, "e3dvocUFTE1UWIvtW8qzulnWErI=")
            # err, clid = ts3lib.getClientID(self.schid)
            # err = ts3lib.requestMuteClients(self.schid, [clid])
            # err, smth = ts3lib.getClientNeededPermission(self.schid, "b_client_info_view")
            # err = ts3lib.requestChannelDescription(self.schid, 36)
            # if self.debug: ts3lib.printMessageToCurrentTab('{0} flushed: {1}'.format(self.name, ts3lib.getErrorMessage(err)))
        except:
            ts3lib.printMessageToCurrentTab(traceback.format_exc())