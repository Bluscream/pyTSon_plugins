import ts3lib, ts3defines, re
from copy import deepcopy as copy
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from time import time
from PythonQt.QtCore import QTimer
from traceback import format_exc
from devtools import PluginInstaller, installedPackages
from bluscream import timestamp, parseCommand, sanitize, getServerType, ServerInstanceType

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
        "timestamps": {
            "start": time()
        },
        "assets": {
            "large_text": "TeamSpeak 3",
            "large_image": "logo"
        }
    }

    def __init__(self):
        try: import unidecode
        except ImportError:
            PluginInstaller().installPackages(['unidecode'])
        try: from discoIPC import ipc
        except ImportError:
            PluginInstaller().installPackages(['discoIPC'])
            from discoIPC import ipc
        self.discord = ipc.DiscordIPC("450824928841957386")
        try:
            self.discord.connect()
        except: pass
        self.timer.timeout.connect(self.tick)
        self.timer.setTimerType(2)
        self.timer.start(1000)
        self.update = True
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        (err, status) = ts3lib.getConnectionStatus(schid)
        if status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.updateServer(schid); self.updateChannel(schid); self.updateVoice(schid);self.updateClient(schid)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        self.timer.stop()
        self.discord.disconnect()

    def tick(self):
        try:
            if not self.update: return
            if not self.discord.connected:
                try: self.discord.connect()
                except: pass
            self.discord.update_activity(self.activity)
            self.update = False
            if PluginHost.cfg.getboolean("general", "verbose"): print(self.name, "updated:", self.activity)
        except: # ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
            print(format_exc())

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
            del self.activity["party"]
            self.activity["assets"] = {
                "small_text": "Disconnected",
                "small_image": "",
                "large_text": "TeamSpeak 3",
                "large_image": "logo"
            }
            self.update = True
        elif status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.updateServer(schid); self.updateChannel(schid); self.updateVoice(schid);self.updateClient(schid)

    def updateServer(self, schid, ownID=0):
        if not ownID: (err, ownID) = ts3lib.getClientID(schid)
        (err, name) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
        from unidecode import unidecode
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
            self.activity["assets"]["large_image"] = "logo"
        self.update = True

    def updateChannel(self, schid, ownID=0, ownCID=0):
        if not ownID: (err, ownID) = ts3lib.getClientID(schid)
        if not ownCID: (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        (err, cname) = ts3lib.getChannelVariable(schid, ownCID, ts3defines.ChannelProperties.CHANNEL_NAME)
        name = re.sub(r'^\[[crl\*]spacer(.*)?\]', '', cname, flags=re.IGNORECASE|re.UNICODE)
        from unidecode import unidecode
        self.activity["state"] = unidecode(name)
        (err, clist) = ts3lib.getChannelClientList(schid, ownCID)
        (err, cmax) = ts3lib.getChannelVariable(schid, ownCID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        (err, smax) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_MAXCLIENTS)
        self.activity["party"] = {
            "id": str(ownCID),
            "size": [len(clist), cmax if cmax >= len(clist) else smax] # cmax if cmax else 0
        }
        (err, ip) = ts3lib.getConnectionVariable(schid, ownID, ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
        (err, port) = ts3lib.getConnectionVariable(schid, ownID, ts3defines.ConnectionProperties.CONNECTION_SERVER_PORT)
        self.activity["secrets"] = {
            "join": "ts3server://{}?port={}&cid={}".format(ip, port, ownCID)
        }
        self.update = True

    def updateClient(self, schid):
        (err, name) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        from unidecode import unidecode
        self.activity["assets"]["large_text"] = unidecode(name)

    def updateVoice(self, schid, status=None):
        if not status: (err, status) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_FLAG_TALKING)
        (err, output_activated) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_OUTPUT_HARDWARE)
        (err, output_muted) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_OUTPUT_MUTED)
        (err, input_deactivated) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_INPUT_DEACTIVATED)
        (err, input_muted) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_INPUT_MUTED)
        (err, commander) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER)
        activity = copy(self.activity)
        if not output_activated:
            activity["assets"]["small_text"] = "Output Deactivated"
            activity["assets"]["small_image"] = "hardware_output_muted"
        elif output_muted:
            activity["assets"]["small_text"] = "Output Muted"
            activity["assets"]["small_image"] = "output_muted"
        elif input_deactivated:
            activity["assets"]["small_text"] = "Input Deactivated"
            activity["assets"]["small_image"] = "hardware_input_muted"
        elif input_muted:
            activity["assets"]["small_text"] = "Input Muted"
            activity["assets"]["small_image"] = "input_muted"
        elif status and commander:
            activity["assets"]["small_text"] = "Talking with Channel Commander"
            activity["assets"]["small_image"] = "player_commander_on"
        elif status and not commander:
            activity["assets"]["small_text"] = "Talking"
            activity["assets"]["small_image"] = "player_on"
        elif not status and commander:
            activity["assets"]["small_text"] = "Silent"
            activity["assets"]["small_image"] = "player_commander_off"
        elif not status and not commander:
            activity["assets"]["small_text"] = "Silent"
            activity["assets"]["small_image"] = "player_off"
        if activity != self.activity:
            self.activity = activity
            self.update = True
        del activity

    def onClientSelfVariableUpdateEvent(self, schid, flag, oldValue, newValue):
        props = ts3defines.ClientProperties
        if flag in [props.CLIENT_OUTPUT_HARDWARE,props.CLIENT_OUTPUT_MUTED,props.CLIENT_INPUT_DEACTIVATED,props.CLIENT_INPUT_MUTED,ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER]:
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