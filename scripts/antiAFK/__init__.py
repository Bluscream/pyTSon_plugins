import ts3lib, ts3defines
from random import randint
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
    debug = False
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
                self.timer.stop()
                self.timer = None
                ts3lib.printMessageToCurrentTab('Timer stopped!')
            else:
                self.schid = schid
                err, self.clid = ts3lib.getClientID(schid)
                self.timer.start(randint(30*1000,120*1000))
                ts3lib.printMessageToCurrentTab('Timer started!')

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if fromID == self.clid and targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT and message == self.text: return 1

    def tick(self): ts3lib.requestSendPrivateTextMsg(self.schid, self.text, self.clid)