import ts3lib, ts3defines#, sys
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
    guiLogLvl = logLevel.NONE
    banned_names = ["BAN", "NOT WELCOME"]
    mod_names = ["MOD", "OPERATOR", "ADMIN"] # TODO CHECK
    tabs =  {}

    def __init__(self):
        # sys.setdefaultencoding('utf-8')
        self.ts3host = ts3SessionHost(self)
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        (err, status) = ts3lib.getConnectionStatus(schid)
        self.onConnectStatusChangeEvent(schid, status, err)
        if PluginHost.cfg.getboolean("general", "verbose"):
            i = 1
            for active in PluginHost.active: print(i, active); i += 1
            ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onConnectStatusChangeEvent(self, schid, status, errorNumber):
        if status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            if not schid in self.tabs:
                self.tabs[schid] = {
                    "channelBanGroup": None,
                    "channelModGroup": None
                }
            srv = self.ts3host.getServer(schid)
            srv.requestServerGroupList()
            srv.requestChannelGroupList()
        elif status == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if schid in self.tabs: del self.tabs[schid]

    def onServerGroupListEvent(self, schid, serverGroupID, name, atype, iconID, saveDB):
        if atype != GroupType.REGULAR: return
        srv = self.ts3host.getServer(schid)
        srv.updateServerGroup(serverGroupID, name, iconID)

    def onChannelGroupListEvent(self, schid, channelGroupID, name, atype, iconID, saveDB):
        if atype != GroupType.REGULAR: return
        tab = self.tabs[schid]
        for _name in self.banned_names:
            if _name in name.upper(): tab["channelBanGroup"] = channelGroupID; break
        for _name in self.mod_names:
            if _name in name.upper(): tab["channelModGroup"] = channelGroupID; break
        srv = self.ts3host.getServer(schid)
        srv.updateChannelGroup(channelGroupID, name, iconID)

    def onTalkStatusChangeEvent(self, schid, status, isReceivedWhisper, clientID):
        self.ts3host.getServer(schid).updateTalkStatus(clientID, status, isReceivedWhisper)

    def stop(self): del self.ts3host