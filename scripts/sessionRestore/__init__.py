import ts3lib, os
from json import dump, load
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from bluscream import log, getScriptPath
from ts3defines import LogLevel, ConnectStatus, PluginConnectTab, ERROR_ok, ClientProperties
from traceback import format_exc

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
    _delay = delay
    _tabs = {}
    _timers = []
    backup_file = os.path.join(path, "session.json")
    first = True

    def __init__(self):
        if "aaa_ts3Ext" in PluginHost.active:
            ts3ext = PluginHost.active["aaa_ts3Ext"]
            self.tabs = ts3ext.tabs
            ts3lib.logMessage("{}: Dependency loaded".format(self.name), LogLevel.LogLevel_WARNING, "pyTSon", 0)
            log(self, LogLevel.LogLevel_DEBUG, "[color=orange]{name}[/color] Plugin for pyTSon by [url=https://github.com/{author}]{author}[/url] loaded.".format(name=self.name, author=self.author), 0)
        else:
            retry = 1000
            self.timer.singleShot(retry, self.__init__)
            ts3lib.logMessage("{}: Dependency not yet loaded, retrying in {} second(s)!".format(self.name, retry/1000), LogLevel.LogLevel_WARNING, "pyTSon", 0)

    def stop(self):
        if hasattr(self, "timer"):
            if self.timer.isActive(): self.timer.stop()

    def saveTabs(self):
        tabs = {} # Todo: OrderedDict
        for tab in self.tabs:
            if self.tabs[tab]["status"] == ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
                tabs[tab] = self.tabs[tab]
        if not len(tabs): return
        with open(self.backup_file, 'w') as outfile:
            dump(tabs, outfile)

    def restoreTabs(self):
        try:
            err, schids = ts3lib.getServerConnectionHandlerList()
            if err != ERROR_ok: return
            if len(schids) > 1: return
            for schid in schids:
                (err, status) = ts3lib.getConnectionStatus(schid)
                if err != ERROR_ok: return
                if status != ConnectStatus.STATUS_DISCONNECTED: return
            self._tabs = {};self._timers = []
            with open(self.backup_file) as f:
                self._tabs = load(f)
            i = 0
            self._delay = self.delay
            for tab in self._tabs:
                i += 1
                # if self._tabs[tab]["status"] == ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
                timer = QTimer()
                self._timers.append(timer)
                timer.singleShot(self._delay, self.restoreTab)
                # self.restoreTab(tab)
                self._delay += self.increase
        except: ts3lib.logMessage(format_exc(), LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def restoreTab(self, tab=None):
        try:
            if not tab:
                self._timers.pop(0)
                schid, tab = self._tabs.popitem()
            args = [
                PluginConnectTab.PLUGIN_CONNECT_TAB_NEW_IF_CURRENT_CONNECTED if self.first else PluginConnectTab.PLUGIN_CONNECT_TAB_NEW, # connectTab: int,
                tab["name"], # serverLabel: Union[str, unicode],
                tab["address"], # serverAddress: Union[str, unicode],
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
            if self.first: self.first = False
            print("ts3lib.guiConnect({})".format("\", \"".join(str(x) for x in args)))
            err, schid = ts3lib.guiConnect(args[0],args[1],args[2],args[3],args[4],args[5],args[6],args[7],args[8],args[9],args[10],args[11],args[12], args[13])
            ts3lib.setClientSelfVariableAsString(schid, ClientProperties.CLIENT_INPUT_MUTED, tab["input_muted"])
            ts3lib.setClientSelfVariableAsString(schid, ClientProperties.CLIENT_OUTPUT_MUTED, tab["output_muted"])
            ts3lib.requestChannelSubscribeAll(schid)
        except: ts3lib.logMessage(format_exc(), LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def menuCreated(self):
        if not self.first: return
        self.timer.timeout.connect(self.saveTabs)
        self.timer.setTimerType(2)
        self.timer.start(5000)
        self.restoreTabs()