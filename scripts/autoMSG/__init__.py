from ts3plugin import ts3plugin
from datetime import datetime
import ts3defines, ts3lib
from os import path

class autoMSG(ts3plugin):
    name = "Auto Message"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Auto Message", "")]
    debug = False
    enabled = True
    msg = "Glory to Arstotzka, comrade!"
    uids = ["IXv9Uy3eHpsrRupdMkUTxuTfHQE=","VhFyPHz95ZmWcMRy43rqsdo48RM=","dnKrBFaIJoMeaKfZ4R6wNDrWVRA=","0HKo9jcJKijfg3wBzgvXkGn/u6g=","09RsHejbkOvorPNJQdRnH5Lz3gY="]

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.enabled = not self.enabled
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.toggle))

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.enabled: return
        try:
            (error, _clid) = ts3lib.getClientID(schid)
            if not clientID == _clid and oldChannelID == 0:
                (error, uid) = ts3lib.getClientVariableAsString(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                if uid in self.uids: ts3lib.requestSendPrivateTextMsg(schid, self.msg, clientID)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
