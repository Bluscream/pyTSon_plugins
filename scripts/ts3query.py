from ts3plugin import ts3plugin, PluginHost
import ts3, ts3defines, datetime, ts3query


class ts3query(ts3plugin):
    name = "TS3 Query Console"
    apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Adds a query console to your Teamspeak 3 Client.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Show Query Console", "")]
    hotkeys = []
    debug = False
    toggle = True

    def __init__(self):
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug:
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.toggle = not self.toggle
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.datetime.now())+" Set Auto Channel Commander to [color=yellow]"+str(self.toggle)+"[/color]")

    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        if self.toggle:
            if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHING:
                self.requested = True
                ts3.requestChannelGroupList(ts3.getCurrentServerConnectionHandlerID())
