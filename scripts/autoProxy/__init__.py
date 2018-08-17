import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from PythonQt.QtCore import QTimer
from PythonQt.QtNetwork import QHostAddress
from bluscream import timestamp
from ts3cloud_proxy import TS3CloudProxy

class autoProxy(ts3plugin):
    name = "Automatic Proxy"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.2"
    author = "Bluscream"
    description = "Uses ts3.cloud's ts3proxy service to switch to a proxy on every connection.\nRequires ts3cloud_proxy.py in your include folder!"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    proxied = False
    host = "127.0.0.1"
    port = 9987

    nickname = "Bluscream"
    whitelist = ["127.0.0.1","homeserver","minopia.de"] # all lower case

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTING: return
        if self.proxied: self.proxied = False; return
        err, host, port, pw = ts3lib.getServerConnectInfo(schid)
        if host.lower() in self.whitelist: ts3lib.printMessageToCurrentTab("[color=green]%s is whitelisted, not using proxy!" % host); return
        ip = QHostAddress(host)
        if not ip.isNull():
            if ip.isLoopback(): ts3lib.printMessageToCurrentTab("[color=green]%s is Loopback, not using proxy!" % host); return
            elif ip.isMulticast(): ts3lib.printMessageToCurrentTab("[color=green]%s is Multicast, not using proxy!" % host); return
            elif ip.isLinkLocal(): ts3lib.printMessageToCurrentTab("[color=green]%s is LinkLocal, not using proxy!" % host); return
            # elif ip.isInSubnet(): ts3lib.printMessageToCurrentTab("[color=green]%s is LinkLocal, not using proxy!" % host); return # TODO: Check aginst local subnet
        address = "{}:{}".format(host,port)
        ts3lib.printMessageToCurrentTab("[color=red]Not proxied on %s, disconnecting!"%address)
        ts3lib.stopConnection(schid, "switching to proxy")
        self.host = host;self.port = port;self.pw = pw
        QTimer.singleShot(250, self.proxy)

    def proxy(self):
        proxy = TS3CloudProxy().generateProxy(self.host, self.port)
        # ts3lib.startConnection(schid, identity, proxy[0], proxy[1], nickname, [], "123", "123")
        address = '{}:{}'.format(proxy[0], proxy[1])
        self.proxied = True
        ts3lib.printMessageToCurrentTab("[color=green]Connecting to proxy %s"%address)
        ts3lib.guiConnect(ts3defines.PluginConnectTab.PLUGIN_CONNECT_TAB_CURRENT, address, address, self.pw, self.nickname, "", "", "", "", "", "", "", "", "")