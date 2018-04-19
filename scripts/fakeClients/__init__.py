from ts3plugin import ts3plugin, PluginHost
from random import choice, getrandbits, randint
from bluscream import timestamp, sendCommand, random_string, loadBadges
from PythonQt.QtCore import QTimer
import ts3defines, ts3lib, pytson

class fakeClients(ts3plugin):
    name = "Fake Clients"
    apiVersion = 21
    requestAutoload = False
    version = "1"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "fc"
    infoTitle = None
    path = "scripts/fakeClients"
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Timeout", "%s/ping_4.svg"%path),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "== Hacks ==", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 1, "Disconnect", "%s/disconnect.svg"%path),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 2, "Kick", "%s/kick_server.svg"%path),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 3, "Ban", "%s/ban_client.svg"%path),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 4, "Timeout", "%s/ping_4.svg"%path),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 5, "== Hacks ==", "")
    ]
    hotkeys = []
    timer = QTimer()
    count = 1
    fakeclients = []

    def __init__(self):
        self.timer.timeout.connect(self.tick)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def menuCreated(self):
        if not self.name in PluginHost.active: return
        for id in [0,5]:
            try: ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, id), False)
            except: pass

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            (err, cid) = ts3lib.getChannelOfClient(schid, selectedItemID)
            if menuItemID == 1: sendCommand(self.name, "notifyclientleftview cfid={} ctid=0 reasonid=8 reasonmsg=disconnected clid={}".format(cid, selectedItemID), schid, True, True)
            elif menuItemID == 2: sendCommand(self.name, "notifyclientleftview cfid={} ctid=0 reasonid=5 reasonmsg=kicked clid={} invokerid=0 invokername=Server invokeruid".format(cid, selectedItemID), schid, True, True)
            elif menuItemID == 3: sendCommand(self.name, "notifyclientleftview cfid={} ctid=0 reasonid=6 reasonmsg=ban clid={} invokerid=0 invokername=Server invokeruid bantime=0".format(cid, selectedItemID), schid, True, True)
            elif menuItemID == 4: sendCommand(self.name, "notifyclientleftview cfid={} ctid=0 reasonid=3 reasonmsg=DDoS clid={}".format(cid, selectedItemID), schid, True, True)
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            for client in self.fakeclients:
                sendCommand(self.name, "notifyclientleftview cfid={} ctid=0 reasonid=6 reasonmsg=ban clid={} invokerid=0 invokername=Server invokeruid bantime=0".format(client[1], client[0]), schid, True, True)
            self.fakeclients = []

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if oldChannelID != 0: return # if newChannelID == 0: return
        (err, clid) = ts3lib.getClientID(schid)
        if clientID == clid: return
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if uid.startswith("FakeClient"): return
        sendCommand(self.name, "notifyclientupdated clid={} client_is_channel_commander=1 client_country=JP client_is_recording=1 client_platform=Windoof".format(clientID), schid, True, True)

    def processCommand(self, schid, command):
        clients = 1
        try: clients = int(command)
        except: pass
        self.clients = []
        # (err, clid) = ts3lib.getClientID(schid)
        # (err, cid) = ts3lib.getChannelOfClient(schid, clid)
        (err, clids) = ts3lib.getClientList(schid)
        self.clients.extend(clids)
        e, self.sgroup = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_SERVER_GROUP)
        e, acg = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
        e, dcg = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_ADMIN_GROUP)
        self.cgroups = [acg, dcg]
        timestamp, ret, badges = loadBadges()
        self.badges = []
        for badge in ret:
            self.badges.append(badge)
        if clients > 10:
            self.i = 1
            self.schid = schid
            self.c = clients+1
            self.timer.start(1)
        else:
            for i in range(clients):
                self.addClient(schid)
                i += 1
        return True

    def tick(self):
        if self.i >= self.c: self.timer.stop()
        self.addClient(self.schid)
        self.i += 1

    def addClient(self, schid):
        cmd = "notifycliententerview"
        client = self.fakeClient(schid)
        for k in client:
            if client[k] != "":
                cmd += " {}={}".format(k, client[k])
            else: cmd += " {}".format(k)
        sendCommand(self.name, cmd, schid, True, True)

    def fakeClient(self, schid):
        client = {}
        client["reasonid"] = "0"
        client["cfid"] = "0"
        (err, cids) = ts3lib.getChannelList(schid)
        cid = choice(cids)
        client["ctid"] = cid
        client["client_channel_group_id"] = choice(self.cgroups)
        client["client_servergroups"] = self.sgroup
        client["client_channel_group_inherited_channel_id"] = cid
        client["client_input_muted"] = randint(0,1)
        client["client_output_muted"] = randint(0,1)
        client["client_outputonly_muted"] = randint(0,1)
        client["client_input_hardware"] = randint(0,1)
        client["client_output_hardware"] = randint(0,1)
        client["client_is_recording"] = randint(0,1)
        client["client_talk_request"] = randint(0,1)
        client["client_type"] = 0 # randint(0,1)
        client["client_is_talker"] = randint(0,1)
        client["client_away"] = randint(0,1)
        client["client_is_channel_commander"] = randint(0,1)
        client["client_is_priority_speaker"] = randint(0,1)
        clid = randint(0,65000)
        while clid in self.clients:
            clid = randint(0, 65000)
        client["clid"] = clid
        client["client_database_id"] = randint(0,1000)
        client["client_talk_power"] = randint(0,99999)
        client["client_unread_messages"] = randint(0,10)
        client["client_needed_serverquery_view_power"] = 0 # randint(0,65000)
        client["client_icon_id"] = "0" # = randint(0,65000)
        client["client_unique_identifier"] = "FakeClient#{}".format(self.count) # "{}=".format(random_string(27))
        client["client_nickname"] = random_string(randint(3,30))
        client["client_meta_data"] = random_string(randint(0,1)) # 30
        client["client_away_message"] = random_string(randint(0,10)) # 80
        client["client_flag_avatar"] = "" # = random_string(1)
        client["client_talk_request_msg"] = random_string(randint(0,50))
        client["client_description"] = random_string(randint(0,50))
        client["client_nickname_phonetic"] = random_string(randint(3,30))
        client["client_country"] = random_string(2).upper() # "DE" #
        client["client_badges"] = "overwolf={}:badges={}".format(randint(0,1), choice(self.badges)) # random_string(randint(0,30))
        self.count += 1
        self.clients.append(clid)
        self.fakeclients.append((clid, cid))
        return client