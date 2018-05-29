import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from discordrpc import DiscordIpcClient
from time import time
from PythonQt.QtCore import QTimer
from bluscream import timestamp, parseCommand

class discordify(ts3plugin):
    name = "Discord Rich Presence"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Show off your big Teamspeak cock on Discord"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    discord = None
    update = False
    timer = QTimer()
    activity = {
        "details": "Disconnected",
        "state": "",
        "partySize": 0,
        "partyMax": 0,
        "timestamps": {
            "start": time()
        },
        "assets": {
            "small_text": "Disconnected",
            "small_image": "",
            "large_text": "TeamSpeak 3",
            "large_image": "logo"
        }
    }

    def __init__(self):
        self.discord = DiscordIpcClient.for_platform('450824928841957386')
        #
        self.timer.timeout.connect(self.tick)
        self.timer.setTimerType(2)
        self.timer.start(1000)
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        (err, status) = ts3lib.getConnectionStatus(schid)
        if status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.updateDiscordPresence(schid)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        self.timer.stop()

    def tick(self):
        try:
            if not self.update: return
            self.discord.set_activity(self.activity)
            self.update = False
        except: print("error in discord")

    def currentServerConnectionChanged(self, schid):
        self.onTabChangedEvent(schid)
    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        curschid = ts3lib.getCurrentServerConnectionHandlerID()
        if curschid == schid: self.onTabChangedEvent(schid, newStatus)

    def onTabChangedEvent(self, schid, status=None):
        if status is None: (err, status) = ts3lib.getConnectionStatus(schid)
        if status == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            self.activity["details"] = "Disconnected"
            self.activity["state"] = ""
            self.activity["partySize"] = 0
            self.activity["partyMax"] = 0
            self.activity["assets"] = {
                "small_text": "Disconnected",
                "small_image": "",
                "large_text": "TeamSpeak 3",
                "large_image": "logo"
            }
        elif status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.updateDiscordPresence(schid)

    def updateDiscordPresence(self, schid):
        (err, ownID) = ts3lib.getClientID(schid)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        (err, sname) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
        self.activity["details"] = sname
        (err, cname) = ts3lib.getChannelVariable(schid, ownCID, ts3defines.ChannelProperties.CHANNEL_NAME)
        self.activity["state"] = cname
        (err, clist) = ts3lib.getChannelClientList(schid, ownCID)
        self.activity["partySize"] = len(clist)
        (err, cmax) = ts3lib.getChannelVariable(schid, ownCID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        self.activity["partyMax"] = cmax
        self.update = True

    def onTalkStatusChangeEvent(self, schid, status, isReceivedWhisper, clientID):
        pass

    def onIncomingClientQueryEvent(self, schid, commandText):
        return
        if commandText.split(" ", 1)[0] != "notifyclientupdated": return
        (cmd, params) = parseCommand(commandText)
        if len(params) > 0 and "client_nickname" in params:
            clid = int(params["clid"])
            # (err, ownID) = ts3lib.getClientID(schid)
            # if clid == ownID: return
            (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            if getContactStatus(uid) != ContactStatus.FRIEND: return
            if not self.dynamicSilenceName in params["client_nickname"].lower(): return
            ts3lib.requestSendPrivateTextMsg(schid, "Yes, {}-{}?".format(clientURL(schid, clid), choice(["chan","san"])), clid)
            # ts3lib.printMessageToCurrentTab("{} {}".format(cmd, params)) # ["client_nickname"][1]