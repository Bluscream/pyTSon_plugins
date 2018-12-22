import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from PythonQt.QtCore import QUrl, QTimer, QByteArray
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QHostAddress
from bluscream import timestamp, getScriptPath, inputBox, msgBox
from os import path
from bs4 import BeautifulSoup

class autoProxy(ts3plugin):
    path = getScriptPath(__name__)
    name = "Automatic Proxy"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.2"
    author = "Bluscream"
    description = "Uses ts3.cloud's ts3proxy service to switch to a proxy on every connection."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle %s"%name, "scripts/%s/proxy.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Proxy whitelist", "scripts/%s/whitelist.png"%__name__)
    ]
    hotkeys = []
    proxied = False
    nwmc = QNetworkAccessManager()
    nwmc_resolver = QNetworkAccessManager()
    request = QNetworkRequest(QUrl("https://www.ts3.cloud/ts3proxy"))
    payload = "input={host}:{port}&proxy="
    whitelist_ini = "%s/whitelist.txt" % path
    whitelist = []
    backup = {"address": "127.0.0.1:9987", "nickname": "", "phonetic": "", "token": "", "c": "AFK", "cpw": "123", "pw": "123"}
    enabled = False

    def __init__(self):
        content = []
        if not path.exists(self.whitelist_ini):
            with open(self.whitelist_ini, 'w'): pass
        with open(self.whitelist_ini, encoding="utf-8") as f:
            content = f.readlines()
        self.whitelist = [x.strip() for x in content]
        self.nwmc.connect("finished(QNetworkReply*)", self.reply)
        self.nwmc_resolver.connect("finished(QNetworkReply*)", self.resolveReply)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL: return
        if menuItemID == 0:
            self.enabled = not self.enabled
            if self.enabled: ts3lib.printMessageToCurrentTab("{} > [color=green]Enabled!".format(self.name))
            else: ts3lib.printMessageToCurrentTab("{} > [color=red]Disabled!".format(self.name))
        elif menuItemID == 1:
            err, host, port, pw = ts3lib.getServerConnectInfo(schid)
            host = inputBox(self.name, "Server address:", host)
            if not host: msgBox("Nothing to add!", title=self.name); return
            if host in self.whitelist:
                self.whitelist.remove(host)
                ts3lib.printMessageToCurrentTab("{} > Removed {} from whitelist!".format(self.name,host))
            else:
                self.whitelist.append(host.lower())
                ts3lib.printMessageToCurrentTab("{} > Added {} to whitelist!".format(self.name,host))
            with open(self.whitelist_ini, "a") as myfile:
                myfile.write('\n{0}'.format(host))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if not self.enabled: return
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTING: return
        if self.proxied: self.proxied = False; return
        err, host, port, pw = ts3lib.getServerConnectInfo(schid)
        if host.lower() in self.whitelist: ts3lib.printMessageToCurrentTab("[color=green]%s is whitelisted, not using proxy!" % host); return
        ip = QHostAddress(host)
        if not ip.isNull():
            if ip.isLoopback(): ts3lib.printMessageToCurrentTab("[color=green]%s is Loopback, not using proxy!" % host); return
            elif ip.isMulticast(): ts3lib.printMessageToCurrentTab("[color=green]%s is Multicast, not using proxy!" % host); return
        is_nickname = False
        if not "." in host:
            ts3lib.printMessageToCurrentTab("[color=orange]%s is a server nickname, resolving..." % host)
            self.backup["address"] = host
            is_nickname = True
        if not is_nickname:
            self.backup["address"] = "{}:{}".format(host,port)
            ts3lib.printMessageToCurrentTab("[color=red]Not proxied on %s, disconnecting!"%self.backup["address"])
        ts3lib.stopConnection(schid, "switching to proxy")
        if pw: self.backup["pw"] = pw
        err, nickname = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if not err and nickname: self.backup["nickname"] = nickname
        err, nickname_phonetic = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_NICKNAME_PHONETIC)
        if not err and nickname_phonetic: self.backup["phonetic"] = nickname_phonetic
        err, c = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_DEFAULT_CHANNEL)
        if not err and c: self.backup["c"] = c
        err, cpw = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_DEFAULT_CHANNEL_PASSWORD)
        if not err and cpw: self.backup["cpw"] = cpw
        err, default_token = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_DEFAULT_TOKEN)
        if not err and default_token: self.backup["token"] = default_token
        if is_nickname:
            self.nwmc_resolver.get(QNetworkRequest(QUrl("https://named.myteamspeak.com/lookup?name=%s"%host)))
            return
        self.proxy(host, port)

    def proxy(self, host, port):
        payload = self.payload.format(host=host,port=port)
        self.nwmc.post(self.request, payload)

    def reply(self, reply):
        page = reply.readAll().data().decode('utf-8')
        soup = BeautifulSoup(page, features="html.parser")
        div_alert = soup.find("div", {"class": "alert alert-success alert-dismissable"})
        proxy_adress = div_alert.find("center").find("b").text
        ts3lib.printMessageToCurrentTab("[color=green]Connecting to proxy %s"%proxy_adress)
        self.proxied = True
        ts3lib.guiConnect(ts3defines.PluginConnectTab.PLUGIN_CONNECT_TAB_CURRENT,
            self.backup["address"], # Name
            proxy_adress, # Address
            self.backup["pw"], # Server Password
            self.backup["nickname"], # Nickname
            self.backup["c"], # Channel Path
            self.backup["cpw"], # Channel Password
            "", "", "", "", "",
            self.backup["token"], # Privilege Key
            self.backup["phonetic"] # Phonetic Nickname
        )

    def resolveReply(self, reply):
        resolved = reply.readAll().data().decode('utf-8').strip()
        ts3lib.printMessageToCurrentTab("[color=green]Resolved server nickname %s to %s" % (self.backup["address"], resolved))
        resolved = resolved.split(":")
        self.proxy(resolved[0], resolved[1] if len(resolved) > 1 else 9987)