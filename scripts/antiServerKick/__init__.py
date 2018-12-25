import ts3lib, ts3defines
from datetime import datetime
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from bluscream import timestamp, log
from ts3defines import LogLevel, TextMessageTargetMode

class antiServerKick(ts3plugin):
    name = "Anti Server Kick"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Auto rejoin servers after you got kicked."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = False
    whitelistUIDs = ["serveradmin"]
    delay = 2500
    timer = QTimer()
    tabs = {}
    schid = 0

    def __init__(self):
        if "aaa_ts3Ext" in PluginHost.active:
            self.tabs = PluginHost.active["aaa_ts3Ext"].tabs
            ts3lib.logMessage("{}: Dependency loaded".format(self.name), ts3defines.LogLevel.LogLevel_WARNING, "pyTSon", 0)
        else:
            retry = 1000
            self.timer.singleShot(retry, self.__init__)
            # ts3lib.logMessage("{}: Dependency not yet loaded, retrying in {} second(s)!".format(self.name, retry/1000), ts3defines.LogLevel.LogLevel_WARNING, "pyTSon", 0)
            return
        log(self, LogLevel.LogLevel_DEBUG, "[color=orange]{0}[/color] Plugin for pyTSon by [url=https://github.com/{1}]{1}[/url] loaded.".format(self.name, self.author), 0)

    def onClientKickFromServerEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        if kickerID == clientID: return
        if schid not in self.tabs: return
        if clientID != self.tabs[schid]["clid"]: return
        if kickerUniqueIdentifier in self.whitelistUIDs: return
        if self.delay > 0:
            self.schid = schid
            QTimer.singleShot(self.delay, self.reconnect)
        else: self.reconnect(schid)

    def reconnect(self, schid=None):
        try:
            schid = schid if schid else self.schid
            args = [
                ts3defines.PluginConnectTab.PLUGIN_CONNECT_TAB_NEW_IF_CURRENT_CONNECTED, # connectTab: int,
                self.tabs[schid]["name"], # serverLabel: Union[str, unicode],
                self.tabs[schid]["address"], # serverAddress: Union[str, unicode],
                self.tabs[schid]["pw"], # serverPassword: Union[str, unicode],
                self.tabs[schid]["nick"], # nickname: Union[str, unicode],
                self.tabs[schid]["cpath"], # channel: Union[str, unicode],
                self.tabs[schid]["cpw"], # channelPassword: Union[str, unicode]
                "", # captureProfile: Union[str, unicode],
                "", # playbackProfile: Union[str, unicode]
                "", # hotkeyProfile: Union[str, unicode],
                "Default Sound Pack (Female)", # soundPack
                self.tabs[schid]["uid"], # userIdentity: Union[str, unicode],
                self.tabs[schid]["token"], # oneTimeKey: Union[str, unicode],
                self.tabs[schid]["nick_phonetic"] # phoneticName: Union[str, unicode]
            ]
            print("ts3lib.guiConnect({})".format("\", \"".join(str(x) for x in args)))
            ts3lib.guiConnect(args[0],args[1],args[2],args[3],args[4],args[5],args[6],args[7],args[8],args[9],args[10],args[11],args[12], args[13])
            self.schid = 0
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

