import ts3lib, ts3defines, re
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from discoIPC import ipc
from time import time
from PythonQt.QtCore import QTimer
from traceback import format_exc
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
        "timestamps": {
            "start": time()
        },
        "assets": {
            "large_text": "TeamSpeak 3",
            "large_image": "logo"
        }
    }
    test = {
        'state': 'In the white house.',
        'details': 'The player has to find the secret item that\'s hidden inside the white house, before the time ends.',
        'timestamps': {
            'start': time()
        },
        'assets': {
            'large_image': '32db72f5-826b-4cd7-bfed-a72c3890eccd',
            'large_text': 'Level 4',
            'small_image': 'e76c00bd-a8d7-41e8-aa34-92a843e03e5e',
            'small_text': 'Salvation',
        },
        'party': {
            'id': 'dcb5c08f-0bae-4e1c-98c0-09343939c965',
            'size': [1, 2]
        },
        'secrets': {
            'match': 'MmhuZToxMjMxMjM6cWl3amR3MWlqZA==',
            'spectate': 'MTIzNDV8MTIzNDV8MTMyNDU0',
            'join': 'MTI4NzM0OjFpMmhuZToxMjMxMjM=',
        },
        'instance': True,
}

    def __init__(self):
        self.discord = ipc.DiscordIPC("450824928841957386")
        self.discord.connect()
        self.timer.timeout.connect(self.tick)
        self.timer.setTimerType(2)
        self.timer.start(1000)
        self.update = True
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        (err, status) = ts3lib.getConnectionStatus(schid)
        if status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.updateServer(schid); self.updateChannel(schid); self.updateVoice(schid);self.updateClient(schid)
        else: self.update = True
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        self.timer.stop()
        self.discord.disconnect()

    def tick(self):
        try:
            if not self.update: return
            self.discord.update_activity(self.activity)
            self.update = False
            print("updated discord with ", self.activity)
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
            if hasattr(self.activity, "state"): del self.activity["state"]
            if hasattr(self.activity, "party"): del self.activity["party"]
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
        (err, sname) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
        self.activity["details"] = sname
        self.update = True

    def updateChannel(self, schid, ownID=0, ownCID=0):
        if not ownID: (err, ownID) = ts3lib.getClientID(schid)
        if not ownCID: (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        (err, cname) = ts3lib.getChannelVariable(schid, ownCID, ts3defines.ChannelProperties.CHANNEL_NAME)
        cname = re.sub(r'^\[[crl]spacer(\d+)?\]', '', cname, flags=re.IGNORECASE|re.UNICODE)
        self.activity["state"] = cname
        (err, clist) = ts3lib.getChannelClientList(schid, ownCID)
        (err, cmax) = ts3lib.getChannelVariable(schid, ownCID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        (err, smax) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_MAXCLIENTS)
        self.activity["party"] = {
            "id": str(ownCID),
            "size": [len(clist), cmax if cmax > -1 else smax] # cmax if cmax else 0
        }
        self.update = True

    def updateClient(self, schid):
        (err, name) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        self.activity["assets"]["large_text"] = name

    def updateVoice(self, schid, status=None):
        if not status: (err, status) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_FLAG_TALKING)
        (err, output_activated) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_OUTPUT_HARDWARE)
        (err, output_muted) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_OUTPUT_MUTED)
        (err, input_deactivated) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_INPUT_DEACTIVATED)
        (err, input_muted) = ts3lib.getClientSelfVariable(schid,ts3defines.ClientProperties.CLIENT_INPUT_MUTED)
        (err, commander) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER)
        if not output_activated:
            self.activity["assets"]["small_text"] = "Output Deactivated"
            self.activity["assets"]["small_image"] = "hardware_output_muted"
        elif output_muted:
            self.activity["assets"]["small_text"] = "Output Muted"
            self.activity["assets"]["small_image"] = "output_muted"
        elif input_deactivated:
            self.activity["assets"]["small_text"] = "Input Deactivated"
            self.activity["assets"]["small_image"] = "hardware_input_muted"
        elif input_muted:
            self.activity["assets"]["small_text"] = "Input Muted"
            self.activity["assets"]["small_image"] = "input_muted"
        elif status and commander:
            self.activity["assets"]["small_text"] = "Talking with Channel Commander"
            self.activity["assets"]["small_image"] = "player_commander_on"
        elif status and not commander:
            self.activity["assets"]["small_text"] = "Talking"
            self.activity["assets"]["small_image"] = "player_on"
        elif not status and commander:
            self.activity["assets"]["small_text"] = "Silent"
            self.activity["assets"]["small_image"] = "player_commander_off"
        elif not status and not commander:
            self.activity["assets"]["small_text"] = "Silent"
            self.activity["assets"]["small_image"] = "player_off"
        self.update = True

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