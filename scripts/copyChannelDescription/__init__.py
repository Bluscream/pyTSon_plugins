import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.Qt import QApplication
from collections import OrderedDict

class joinChannel(ts3plugin):
    name = "Copy Channel Description"
    apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = False
    version = "1.0"
    author = "Exp"
    description = "Copy Channel Descriptions"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Print all Channels", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 1, "Copy Description", "")
    ]
    hotkeys = []
    debug = False

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, channel):
        if menuItemID == 0:
            err, cids = ts3lib.getChannelList(schid)
            channels = dict()
            for cid in cids:
                (err, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
                (err, order) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_ORDER)
                if err == ts3defines.ERROR_ok and name: channels[order] = name
            channels = OrderedDict(sorted(channels.items(), key=lambda t: t[0]))
            for name in channels.values():
                ts3lib.printMessageToCurrentTab(name)
        elif menuItemID == 1:
            description = ts3lib.getChannelVariableAsString(schid, channel, ts3defines.ChannelProperties.CHANNEL_DESCRIPTION)[1]
            ts3lib.printMessageToCurrentTab(description)
            QApplication.clipboard().setText(description)