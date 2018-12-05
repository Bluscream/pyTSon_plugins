import ts3lib, ts3defines, re
# from copy import deepcopy as copy
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
# from time import time
from datetime import datetime
from PythonQt.QtCore import QTimer
# from traceback import format_exc
from devtools import PluginInstaller, installedPackages
from bluscream import timestamp, parseCommand, sanitize, getServerType, ServerInstanceType

# startTime = datetime.utcnow()

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
    tabs = {}
    activity = {
        "details": "Disconnected",
        "timestamps": {},
        "assets": {
            "large_text": "TeamSpeak 3",
            "large_image": "logo"
        }
    }

    def timestamp(self):
        return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

    def __init__(self):
        try: import unidecode
        except ImportError:
            PluginInstaller().installPackages(['unidecode'])
        try: from discoIPC import ipc
        except ImportError:
            PluginInstaller().installPackages(['discoIPC'])
            from discoIPC import ipc
        self.discord = ipc.DiscordIPC("504997049226362891") # 450824928841957386
        try: self.discord.connect()
        except: ts3lib.logMessage("Discord not running!", ts3defines.LogLevel.LogLevel_WARNING, "pyTSon Discord Rich Presence", 0)
        self.timer.timeout.connect(self.tick)
        self.timer.setTimerType(2)
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        self.onTabChangedEvent(schid)
        self.timer.start(1000)
        """
        (err, status) = ts3lib.getConnectionStatus(schid)
        if status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.updateServer(schid); self.updateChannel(schid); self.updateVoice(schid);self.updateClient(schid)
        """
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        self.timer.stop()
        if self.discord.connected: self.discord.disconnect()

    def tick(self):
        if not self.update: return
        try:
            if not self.discord.connected: self.discord.connect()
            self.discord.update_activity(self.activity)
        except: pass
        self.update = False
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.name, "updated:", self.activity)

    def currentServerConnectionChanged(self, schid):
        self.onTabChangedEvent(schid)
    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        curschid = ts3lib.getCurrentServerConnectionHandlerID()
        if curschid == schid: self.onTabChangedEvent(schid, newStatus)
    def onTabChangedEvent(self, schid, status=None):
        if status is None: (err, status) = ts3lib.getConnectionStatus(schid)
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.name, schid, status)
        if status == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if schid in self.tabs: del self.tabs[schid]
            self.activity["timestamps"]["start"] = self.timestamp()
            self.activity["details"] = "Disconnected"
            self.activity["state"] = ""
            if hasattr(self.activity, "party"): del self.activity["party"]
            self.activity["assets"] = {
                "small_text": "Disconnected",
                "small_image": "",
                "large_text": "TeamSpeak 3",
                "large_image": "logo"
            }
            self.update = True
        elif status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            if schid in self.tabs:
                self.activity["timestamps"]["start"] = self.tabs[schid]
            else:
                start = self.timestamp()
                self.tabs[schid] = start
                if PluginHost.cfg.getboolean("general", "verbose"): print(self.name, "self.tabs[schid]", self.tabs[schid])
                self.activity["timestamps"]["start"] = start
            self.updateServer(schid); self.updateChannel(schid); self.updateVoice(schid);self.updateClient(schid)

    def updateServer(self, schid, ownID=0):
        from unidecode import unidecode
        if not ownID: (err, ownID) = ts3lib.getClientID(schid)
        (err, name) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
        self.activity["details"] = unidecode(name)
        server_type = getServerType(schid)
        if server_type == ServerInstanceType.TEASPEAK:
            self.activity["assets"]["large_text"] = "TeaSpeak"
            self.activity["assets"]["large_image"] = "teaspeak"
        elif server_type == ServerInstanceType.VANILLA:
            self.activity["assets"]["large_text"] = "TeamSpeak 3"
            self.activity["assets"]["large_image"] = "teamspeak"
        elif server_type == ServerInstanceType.SDK:
            self.activity["assets"]["large_text"] = "TeamSpeak 3 SDK"
            self.activity["assets"]["large_image"] = "teamspeak"
        else:
            self.activity["assets"]["large_text"] = "Unknown"
            self.activity["assets"]["large_image"] = "broken_image"
        self.update = True

    def updateChannel(self, schid, ownID=0, ownCID=0):
        if not ownID: (err, ownID) = ts3lib.getClientID(schid)
        if not ownCID: (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        (err, cname) = ts3lib.getChannelVariable(schid, ownCID, ts3defines.ChannelProperties.CHANNEL_NAME)
        name = re.sub(r'^\[[crl\*]spacer(.*)?\]', '', cname, flags=re.IGNORECASE|re.UNICODE)
        from unidecode import unidecode
        self.activity["state"] = unidecode(name)
        clients = len(ts3lib.getChannelClientList(schid, ownCID)[1])
        # (err, clients) = ts3lib.getChannelVariable(schid, ts3defines.ChannelPropertiesRare.)
        (err, cmax) = ts3lib.getChannelVariable(schid, ownCID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        if cmax >= clients:
            if PluginHost.cfg.getboolean("general", "verbose"): print("cmax",cmax,">=","clients",clients)
            if not "party" in self.activity: self.activity["party"] = {}
            self.activity["party"]["size"] = [clients, cmax]
        else:
            (err, smax) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_MAXCLIENTS)
            # (err, clients) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_CLIENTS_ONLINE)
            # clients = len(ts3lib.getClientList(schid)[1])
            self.activity["party"] = { "size": [clients, smax] }
        (err, ip) = ts3lib.getConnectionVariable(schid, ownID, ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
        (err, port) = ts3lib.getConnectionVariable(schid, ownID, ts3defines.ConnectionProperties.CONNECTION_SERVER_PORT)
        self.activity["secrets"] = { "join": "ts3server://{}?port={}&cid={}".format(ip, port, ownCID) }
        self.update = True

    def updateClient(self, schid):
        (err, name) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        from unidecode import unidecode
        self.activity["assets"]["large_text"] = unidecode(name)

    def updateVoice(self, schid, status=None):
        curschid = ts3lib.getCurrentServerConnectionHandlerID()
        if schid != curschid: return
        if not status: (err, status) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_FLAG_TALKING)
        (err, afk) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_AWAY)
        (err, output_activated) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_OUTPUT_HARDWARE)
        (err, output_muted) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_OUTPUT_MUTED)
        (err, input_activated) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_INPUT_HARDWARE)
        (err, input_muted) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_INPUT_MUTED)
        (err, commander) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER)
        if PluginHost.cfg.getboolean("general", "verbose"):
            print("CLIENT_AWAY",afk,"CLIENT_OUTPUT_HARDWARE",output_activated,"CLIENT_OUTPUT_MUTED",output_muted,"CLIENT_INPUT_HARDWARE",input_activated,"CLIENT_INPUT_MUTED",input_muted)
        if afk:
            self.activity["assets"]["small_text"] = "Away From Keyboard"
            self.activity["assets"]["small_image"] = "away"
            self.update = True
        elif not output_activated:
            self.activity["assets"]["small_text"] = "Output Deactivated"
            self.activity["assets"]["small_image"] = "hardware_output_muted"
            self.update = True
        elif output_muted:
            self.activity["assets"]["small_text"] = "Output Muted"
            self.activity["assets"]["small_image"] = "output_muted"
            self.update = True
        elif not input_activated:
            self.activity["assets"]["small_text"] = "Input Deactivated"
            self.activity["assets"]["small_image"] = "hardware_input_muted"
            self.update = True
        elif input_muted:
            self.activity["assets"]["small_text"] = "Input Muted"
            self.activity["assets"]["small_image"] = "input_muted"
            self.update = True
        elif status and commander:
            self.activity["assets"]["small_text"] = "Talking with Channel Commander"
            self.activity["assets"]["small_image"] = "player_commander_on"
            self.update = True
        elif status and not commander:
            self.activity["assets"]["small_text"] = "Talking"
            self.activity["assets"]["small_image"] = "player_on"
            self.update = True
        elif not status and commander:
            self.activity["assets"]["small_text"] = "Silent"
            self.activity["assets"]["small_image"] = "player_commander_off"
            self.update = True
        elif not status and not commander:
            self.activity["assets"]["small_text"] = "Silent"
            self.activity["assets"]["small_image"] = "player_off"
            self.update = True

    def onClientSelfVariableUpdateEvent(self, schid, flag, oldValue, newValue):
        props = ts3defines.ClientProperties; rare = ts3defines.ClientPropertiesRare
        if flag in [
            props.CLIENT_OUTPUT_HARDWARE, props.CLIENT_OUTPUT_MUTED,
            props.CLIENT_INPUT_DEACTIVATED, props.CLIENT_INPUT_HARDWARE, props.CLIENT_INPUT_MUTED,
            rare.CLIENT_IS_CHANNEL_COMMANDER, rare.CLIENT_AWAY
        ]:
            self.updateVoice(schid)
        elif flag == props.CLIENT_NICKNAME: self.updateClient(schid)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID == clientID: self.updateChannel(schid, ownID)

    def onClientMoveMovedEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID == clientID: self.updateChannel(schid, ownID)

    def onClientKickFromChannelEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID == clientID: self.updateChannel(schid, ownID)

    def onTalkStatusChangeEvent(self, schid, status, isReceivedWhisper, clientID):
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID == clientID: self.updateVoice(schid, status)