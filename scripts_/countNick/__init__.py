import ts3defines, ts3lib
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtCore import QTimer


class countNick(ts3plugin):
    name = "Count Nickname"

    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Auto incrementing nickname", "")]
    hotkeys = []
    timer = None
    debug = False
    prefix = "Ich bin "
    suffix = " jahre alt"
    count = 0

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            if self.timer == None:
                self.timer = QTimer()
                self.timer.timeout.connect(self.tick)
            if self.timer.isActive():
                self.timer.stop()
                self.timer = None
                ts3lib.printMessageToCurrentTab('Timer stopped!')
            else:
                self.timer.start(3000)
                ts3lib.printMessageToCurrentTab('Timer started!')
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.toggle))

    def tick(self,schid=0, clid=0):
        if schid == 0: schid = ts3lib.getCurrentServerConnectionHandlerID()
        if schid == 0: return
        _newnick = '%s%s%s'%(self.prefix, self.count, self.suffix)
        if self.debug: ts3lib.printMessageToCurrentTab('Tick %s: '%self.count + _newnick)
        ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, _newnick)
        ts3lib.flushClientSelfUpdates(schid)
        self.count += 3