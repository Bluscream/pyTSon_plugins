# coding=utf-8
from datetime import datetime
from ts3plugin import ts3plugin
import ts3lib as ts3
import ts3defines, json
from PythonQt.QtCore import QUrl
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class notify(ts3plugin):
    name = "Notifier"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Automatically notifies other clients about:\n\n○ Outdated Clients\n○ Unread Offline Messages.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle "+name, "")]
    hotkeys = []
    debug = False
    toggle = True
    requested = False
    checkOutdatedVersion = True
    checkUnreadMessages = True
    blacklist = ["QTRtPmYiSKpMS8Oyd4hyztcvLqU="]

    versions = {
        "clientver": "3.1.6",
        "clientrev": 1502873983,
        "serverver": "3.0.13.8",
        "serverrev": 1500452811
    }
    _sent = []

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        self.nwmc = QNetworkAccessManager()
        self.requestVersions()
        if self.debug: ts3.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID != 0: return
        self.toggle = not self.toggle
        ts3.printMessageToCurrentTab('{} Set {} to [color=yellow]{}[/color]'.format(self.timestamp(), self.name, self.toggle))

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.toggle: return
        (error, _clid) = ts3.getClientID(schid)
        if clientID != _clid and oldChannelID == 0:
            self.requested = True
            ts3.requestClientVariables(schid, clientID)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            error, targetVer = ts3.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_VERSION)
            if self.debug: ts3.printMessageToCurrentTab("schid: {} error: {} targetVer: {} targetRev: {} serverRev: {}".format(schid, error, targetVer, self.parseVersion(targetVer), self.versions["serverrev"]))
            if error == ts3defines.ERROR_ok and self.parseVersion(targetVer)["rev"] < self.versions["serverrev"]:
                ts3.printMessageToCurrentTab("[color=red]This server is using a outdated version ({}). It might be vulnerable!".format(targetVer))

    def onUpdateClientEvent(self, schid, clientID, invokerID, invokerName, invokerUniqueIdentifier):
        if not self.requested or not self.toggle: return
        error, _uid = ts3.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if _uid in self.blacklist: return
        self.requested = False
        (error, _uid) = ts3.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if _uid in self._sent: return
        _done = False
        (error, country) = ts3.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_COUNTRY)
        if self.debug: ts3.printMessageToCurrentTab("clid: {} error: {} country: {}".format(clientID, error, country))
        if self.checkOutdatedVersion:
            (error, platform) = ts3.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_PLATFORM)
            if self.debug: ts3.printMessageToCurrentTab("clid: {} error: {} platform: {}".format(clientID, error, platform))
            if not platform in ["Windows", "OSX", "Linux"]: return
            (error, targetVer) = ts3.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_VERSION)
            if self.debug: ts3.printMessageToCurrentTab("clid: {} error: {} targetVer: {}".format(clientID, error, targetVer))
            if error == ts3defines.ERROR_ok:
                current = self.parseVersion(targetVer)
                if current["rev"] < self.versions["clientrev"]:
                    if country in ["DE", "CH", "AT"]:
                        msg = """[color=red]Hinweis[/color]:
Du nutzt eine veraltete Version von Teamspeak ([color=red]{current}[/color]).
Bitte aktualisiere deinen Client auf Version [color=blue]{latest}[/color] um mögliche Sicherheitsrisiken auszuschliessen.
Um zu updaten gehe einfach auf "Hilfe" => "Nach Aktualisierung suchen"
                        """
                    else:
                        msg = """[color=red]Attention[/color]:
You are using a outdated version of Teamspeak ([color=red]{current}[/color]).
Your version is very likely vulnerable to several exploits.
Please update your Client to Version [color=blue]{latest}[/color]
To update click on "Help" => "Check for Update
                        """
                    ts3.requestSendPrivateTextMsg(schid, msg.format(current=current["ver"], latest=self.versions["clientver"]), clientID)
                    _done = True
        if self.checkUnreadMessages:
            (error, platform) = ts3.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_PLATFORM)
            if self.debug: ts3.printMessageToCurrentTab("clid: {} error: {} platform: {}".format(clientID, error, platform))
            if platform in ["Android", "iOS"]: return
            (error, messages) = ts3.getClientVariableAsInt(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_UNREAD_MESSAGES)
            if self.debug: ts3.printMessageToCurrentTab("clid: {} error: {} messages: {}".format(clientID, error, messages))
            if messages > 0:
                if country in ["DE", "CH", "AT"]:
                    msg = """[color=orange]Hinweis[/color]:
Du hast [color=blue]%s[/color] ungelesene Offline Nachrichte(n).
Du kannst sie nachlesen indem du auf \"Extras\" => \"Offline Nachrichten\" klickst oder einfach [STRG]+[O] auf deiner Tastatur drückst.
                    """
                else:
                    msg = """[color=orange]Reminder[/color]:
You have [color=blue]%s[/color] unread offline message(s).
You can read them by clicking on \"Tools\" => \"Offline Messages\" or pressing [CTRL]+[O] on your keyboard.
                    """
                ts3.requestSendPrivateTextMsg(schid, msg % messages, clientID)
                _done = True
            if _done:
                self._sent.extend([_uid])
                (err, _ownuid) = ts3.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                close = ts3.clientChatClosed(schid, _ownuid, clientID)
                if self.debug: ts3.printMessageToCurrentTab("\nSCHID: {}\nownUID: {}\nclientID: {}\nclientUID: {}\nclosed: {}\nerrorid: {}".format(schid, _ownuid, clientID, _uid, close == ts3defines.ERROR_ok, close))

    @staticmethod
    def parseVersion(ver):
        ver = ver.split(" ")
        return { "ver": ver[0], "rev": int(ver[2].split("]")[0]) }

    def requestVersions(self):
        self.nwmc.connect("finished(QNetworkReply*)", self.onVersionReply)
        self.nwmc.get(QNetworkRequest(QUrl("https://api.planetteamspeak.com/updatecheck/")))

    def onVersionReply(self, reply):
        self.versions = json.loads(reply.readAll().data().decode('utf-8'))["result"]