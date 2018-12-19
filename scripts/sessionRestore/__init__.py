import ts3lib, os
from json import dump, load
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from bluscream import log, getScriptPath
from ts3defines import LogLevel, ConnectStatus, PluginConnectTab, ERROR_ok

class sessionRestore(ts3plugin):
    path = getScriptPath(__name__)
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
    delay = 500
    increase = 2000
    ts3host = None
    tabs = {}
    _tabs = {}
    backup_file = os.path.join(path, "session.json")
    first = True

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
        tabs = {}
        for tab in self.tabs:
            if self.tabs[tab]["status"] == ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
                tabs[tab] = self.tabs[tab]
        if not len(tabs): return
        with open(self.backup_file, 'w') as outfile:
            dump(tabs, outfile)

    def restoreTabs(self):
        err, schids = ts3lib.getServerConnectionHandlerList()
        if err != ERROR_ok: return
        if len(schids) > 1: return
        for schid in schids:
            (err, status) = ts3lib.getConnectionStatus(schid)
            if err != ERROR_ok: return
            if status != ConnectStatus.STATUS_DISCONNECTED: return
        self._tabs = {}
        self.restoretimers = []
        with open(self.backup_file) as f:
            self._tabs = load(f)
        for tab in self._tabs:
            # if self._tabs[tab]["status"] == ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            QTimer().singleShot(self.delay, self.restoreTab)
            self.delay += self.increase

    def restoreTab(self):
        tab = self._tabs.pop(0)
        print("Restoring tab: {0}".format(tab))
        args = [
            PluginConnectTab.PLUGIN_CONNECT_TAB_NEW_IF_CURRENT_CONNECTED if self.first else PluginConnectTab.PLUGIN_CONNECT_TAB_NEW, # connectTab: int,
            tab["name"], # serverLabel: Union[str, unicode],
            '{}:{}'.format(tab["host"], tab["port"]) if hasattr(tab, 'port') else tab["host"], # serverAddress: Union[str, unicode],
            tab["pw"], # serverPassword: Union[str, unicode],
            tab["nick"], # nickname: Union[str, unicode],
            tab["cpath"], # channel: Union[str, unicode],
            tab["cpw"], # channelPassword: Union[str, unicode]
            "", # captureProfile: Union[str, unicode],
            "", # playbackProfile: Union[str, unicode]
            "", # hotkeyProfile: Union[str, unicode],
            "Default Sound Pack (Female)", # soundPack
            tab["uid"], # userIdentity: Union[str, unicode],
            tab["token"], # oneTimeKey: Union[str, unicode],
            tab["nick_phonetic"] # phoneticName: Union[str, unicode]
        ]
        print("ts3lib.guiConnect({})".format("\", \"".join(str(x) for x in args)))
        ts3lib.guiConnect(args[0],args[1],args[2],args[3],args[4],args[5],args[6],args[7],args[8],args[9],args[10],args[11],args[12], args[13])
        if self.first: self.first = False