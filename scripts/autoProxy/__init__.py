import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from PythonQt.QtCore import QTimer
from bluscream import timestamp
from ts3cloud_proxy import TS3CloudProxy

class autoProxy(ts3plugin):
    name = "Automatic Proxy"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    proxied = False
    host = "127.0.0.1"
    port = 9987

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTING: return
        if self.proxied: self.proxied = False; return
        err, self.host, self.port, self.pw = ts3lib.getServerConnectInfo(schid)
        address = "{}:{}".format(self.host,self.port)
        ts3lib.printMessageToCurrentTab("not proxied on %s, disconnecting!"%address)
        ts3lib.stopConnection(schid, "switching to proxy")
        QTimer.singleShot(250, self.proxy)

    def proxy(self):
        proxy = TS3CloudProxy().generateProxy(self.host, self.port)
        # ts3lib.startConnection(schid, identity, proxy[0], proxy[1], nickname, [], "123", "123")
        address = '{}:{}'.format(proxy[0], proxy[1])
        self.proxied = True
        ts3lib.printMessageToCurrentTab("connecting to proxy %s"%address)
        ts3lib.guiConnect(ts3defines.PluginConnectTab.PLUGIN_CONNECT_TAB_CURRENT, address, address, self.pw, "Bluscream", "", "", "", "", "", "", "", "", "")