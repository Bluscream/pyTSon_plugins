import pytson, ts3lib, ts3defines
from configparser import ConfigParser
from ts3plugin import ts3plugin, PluginHost
from datetime import datetime
from PythonQt.QtCore import QTimer
from bluscream import timestamp, intList, getContactStatus, ContactStatus, clientURL, getScriptPath, loadCfg

class guestLounge(ts3plugin):
    path = getScriptPath(__name__)
    name = "Guest Lounges"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = []
    timer = QTimer()
    ts3host = None
    """
    cfg = ConfigParser()
    cfg["9lBVIDJRSSgAGy+cWJgNlUQRd64="] = { "enabled": True }
    """

    def __init__(self):
        if "aaa_ts3Ext" in PluginHost.active:
            ts3ext = PluginHost.active["aaa_ts3Ext"]
            self.ts3host = ts3ext.ts3host
            self.tabs = ts3ext.tabs
        else:
            retry = 1000
            self.timer.singleShot(retry, self.__init__)
            ts3lib.printMessageToCurrentTab("{}: [color=red]Dependency not yet loaded, retrying in {} second(s)!".format(self.name, retry/1000))
            return
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def stop(self):
        if hasattr(self, "timer"):
            if self.timer.isActive(): self.timer.stop()
            del self.timer

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        client = self.ts3host.getUser(schid, clid)
        if client.server.me.channel.cid
        if not client.server.me.getChannelGroupId() in [self.tabs[schid]["channelModGroup"], client.server.defaultChannelAdminGroup]: return
        if clientID in self.waiting and (newChannelID == 0 or newChannelID == self.mychan):
            # if newChannelID == self.mychan:
                # (err, dbid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
            ts3lib.printMessage(schid, "{}: [color=orange]Removing channel mod from {}".format(self.name, self.waiting[clientID] if newChannelID == 0 else clientURL(schid, clientID)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
            ts3lib.requestSetClientChannelGroup(schid, [self.sgid_guest], [self.mychan], [self.waiting[clientID]])
            del self.waiting[clientID]
            return
        if newChannelID == 0 or oldChannelID != 0: return
        (err, sgids) = ts3lib.getClientVariableAsString(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        if not self.sgid_guest in intList(sgids): return
        # TODO Any way to get the cgid in another channel?
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if getContactStatus(uid) == ContactStatus.BLOCKED:
            ts3lib.printMessage(schid, "{}: [color=red]Not allowing blocked user {} in your channel.".format(self.name, clientURL(schid, clientID)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
            return
        (err, dbid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        self.waiting[clientID] = dbid
        ts3lib.printMessage(schid, "{}:  [color=green]Found new guest {} giving him channel mod until he's here ;)".format(self.name, clientURL(schid, clientID)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
        ts3lib.requestSetClientChannelGroup(schid, [self.cgid_mod], [self.mychan], [dbid])