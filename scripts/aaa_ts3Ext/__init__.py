import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp, GroupType
from ts3Ext import ts3SessionHost, logLevel

class aaa_ts3Ext(ts3plugin):
    name = "aaa_ts3Ext"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "ts3Ext library implementation"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    guiLogLvl = logLevel.ALL

    def __init__(self):
        self.ts3host = ts3SessionHost(self)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onServerGroupListEvent(self, schid, serverGroupID, name, atype, iconID, saveDB):
        if atype != GroupType.REGULAR: return
        srv = self.ts3host.getServer(schid)
        srv.updateServerGroup(serverGroupID, name, iconID)

    def onChannelGroupListEvent(self, schid, channelGroupID, name, atype, iconID, saveDB):
        if atype != GroupType.REGULAR: return
        srv = self.ts3host.getServer(schid)
        srv.updateChannelGroup(channelGroupID, name, iconID)

    def stop(self): del self.ts3host