import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from PythonQt.QtCore import QUrl, QTimer, QByteArray
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QHostAddress
from bluscream import timestamp
# from ts3cloud_proxy import TS3CloudProxy
from bs4 import BeautifulSoup

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
    nwmc = QNetworkAccessManager()
    request = QNetworkRequest(QUrl("https://www.ts3.cloud/ts3proxy"))
    payload = "input={host}:{port}&proxy="

    nickname = "Bluscream"
    whitelist = ["127.0.0.1","192.168.2.38","192.168.2.39"] # all lower case

    def __init__(self):
        self.nwmc.connect("finished(QNetworkReply*)", self.reply)
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
        address = "{}:{}".format(host,port)
        ts3lib.printMessageToCurrentTab("[color=red]Not proxied on %s, disconnecting!"%address)
        ts3lib.stopConnection(schid, "switching to proxy")
        err, nick = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        print(err, nick)
        self.pw = pw
        payload = self.payload.format(host=host,port=port)
        self.nwmc.post(self.request, payload)

    def reply(self, reply):
        page = reply.readAll().data().decode('utf-8')
        soup = BeautifulSoup(page, features="html.parser")
        div_alert = soup.find("div", {"class": "alert alert-success alert-dismissable"})
        proxy_adress = div_alert.find("center").find("b").text
        self.proxied = True
        ts3lib.printMessageToCurrentTab("[color=green]Connecting to proxy %s"%proxy_adress)
        ts3lib.guiConnect(ts3defines.PluginConnectTab.PLUGIN_CONNECT_TAB_CURRENT, proxy_adress, proxy_adress, self.pw, self.nickname, "", "", "", "", "", "", "", "", "")