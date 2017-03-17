import ts3defines, ts3lib
from ts3plugin import ts3plugin
from datetime import datetime

class autoTPRequest(ts3plugin):
    name = "Auto Talk Power Request"
    apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Automatically request talk power when switching channels.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Auto Talk Power", "")]
    hotkeys = []
    debug = False
    toggle = True
    msg = "Auto Talk Power Request"

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.toggle = not self.toggle
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.toggle))

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.toggle: return
        (error, ownid) = ts3lib.getClientID(schid)
        if ownid == clientID:
            try:
                (error, ntp) = ts3lib.getChannelVariableAsInt(schid, newChannelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
                if self.debug: ts3lib.printMessageToCurrentTab('error: {0} | ntp: {1}'.format(error,ntp))
                if ntp < 1: return
                (error, tp) = ts3lib.getClientVariableAsInt(schid, ownid, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
                if self.debug: ts3lib.printMessageToCurrentTab('error: {0} | tp: {1}'.format(error,tp))
                if not tp: ts3lib.requestIsTalker(schid, True, self.msg)
            except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0);return