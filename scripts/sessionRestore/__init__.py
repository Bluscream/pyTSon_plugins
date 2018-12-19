import ts3lib
from json import dump, dumps
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from bluscream import timestamp, log
from ts3defines import LogLevel, ConnectStatus, ClientProperties, VirtualServerProperties, PluginConnectTab, ERROR_ok

class sessionRestore(ts3plugin):
    name = "Session Restore"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Restores your last session on startup"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    timer = QTimer()
    delay = 2500
    ts3host = None
    tabs = {}

    def __init__(self):
        if "aaa_ts3Ext" in PluginHost.active:
            ts3ext = PluginHost.active["aaa_ts3Ext"]
            self.tabs = ts3ext.tabs
            self.timer.timeout.connect(self.saveTabs)
            self.timer.setTimerType(2)
            self.timer.start(5000)
            ts3lib.logMessage("{}: Dependency loaded".format(self.name), LogLevel.LogLevel_WARNING, "pyTSon", 0)
        else:
            retry = 1000
            self.timer.singleShot(retry, self.__init__)
            ts3lib.logMessage("{}: Dependency not yet loaded, retrying in {} second(s)!".format(self.name, retry/1000), LogLevel.LogLevel_WARNING, "pyTSon", 0)
            return
        log(self, LogLevel.LogLevel_DEBUG, "[color=orange]{name}[/color] Plugin for pyTSon by [url=https://github.com/{author}]{author}[/url] loaded.".format(name=self.name, author=self.author), 0)
        self.restoreTabs()

    def stop(self):
        if hasattr(self, "timer"):
            if self.timer.isActive(): self.timer.stop()

    def saveTabs(self):
        print(self.tabs)
        print(dumps(self.tabs))
        with open('data.json', 'w') as outfile:
            dump(self.tabs, outfile)

    def restoreTabs(self):
        err, schids = ts3lib.getServerConnectionHandlerList()
        if err != ERROR_ok: return
        if len(schids) > 1: return
        for schid in schids:
            (err, status) = ts3lib.getConnectionStatus(schid)
            if err != ERROR_ok: return
            if status != ConnectStatus.STATUS_DISCONNECTED: return
        for tab in self.tabs:
            if self.tabs[tab]["status"] == ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
                self.restoreTab(self.tabs[tab])

    def restoreTab(self, tab):
        print("Restoring tab: {0}".format(self.tabs[tab]))
        args = [
            PluginConnectTab.PLUGIN_CONNECT_TAB_NEW_IF_CURRENT_CONNECTED, # connectTab: int,
            self.tabs[tab]["name"], # serverLabel: Union[str, unicode],
            '{}:{}'.format(self.tabs[tab]["host"], self.tabs[tab]["port"]) if hasattr(self.tabs[tab], 'port') else self.tabs[tab]["host"], # serverAddress: Union[str, unicode],
            self.tabs[tab]["pw"], # serverPassword: Union[str, unicode],
            self.tabs[tab]["nick"], # nickname: Union[str, unicode],
            self.tabs[tab]["cpath"], # channel: Union[str, unicode],
            self.tabs[tab]["cpw"], # channelPassword: Union[str, unicode]
            "", # captureProfile: Union[str, unicode],
            "", # playbackProfile: Union[str, unicode]
            "", # hotkeyProfile: Union[str, unicode],
            "Default Sound Pack (Female)", # soundPack
            self.tabs[tab]["uid"], # userIdentity: Union[str, unicode],
            self.tabs[tab]["token"], # oneTimeKey: Union[str, unicode],
            self.tabs[tab]["name_phonetic"] # phoneticName: Union[str, unicode]
        ]
        print("ts3lib.guiConnect({})".format("\", \"".join(str(x) for x in args)))
        ts3lib.guiConnect(args[0],args[1],args[2],args[3],args[4],args[5],args[6],args[7],args[8],args[9],args[10],args[11],args[12], args[13])