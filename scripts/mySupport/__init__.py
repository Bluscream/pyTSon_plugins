import ts3lib, ts3defines, datetime, ts3
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from bluscream import timestamp

class mySupport(ts3plugin):
    name = "my Support"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, "")]
    hotkeys = []
    schid = 1
    schids = []
    waitforchannel = False
    suid = "9lBVIDJRSSgAGy+cWJgNlUQRd64="
    mychan = 1272
    supchan = 0
    myuid = "e3dvocUFTE1UWIvtW8qzulnWErI="
    supchan_props = {
        "name": "Warteraum",
        "maxclients": 1,
        "codec": ts3defines.CodecType.CODEC_SPEEX_NARROWBAND,
        "codec_quality": 0,
        "description": """Channel Owner: [URL=client://0/e3dvocUFTE1UWIvtW8qzulnWErI=~Bluscream]Bluscream[/URL][hr]
[url=https://steamcommunity.com/profiles/76561198022446661][img]https://steamsignature.com/profile/german/76561198022446661.png[/img][/url]
[url=steam://friends/add/76561198022446661]Add as friend[/url] | [url=https://steamcommunity.com/profiles/76561198022446661/games/?tab=all&games_in_common=1]Common games[/url] | [url=https://steamdb.info/calculator/76561198022446661/?cc=eu]Account Value[/url] | [url=https://steamcommunity.com/tradeoffer/new/?partner=62180933&token=fSMYHMGM]Trade[/url]""",
        "permissions": {
            "i_channel_needed_modify_power": 75,
            "i_channel_needed_delete_power": 75,
            "i_channel_needed_join_power": 1,
            "i_channel_needed_subscribe_power": 75,
            "i_channel_needed_description_view_power": 1,
            "i_channel_needed_permission_modify_power": 75,
            "i_client_needed_talk_power": 1337,
            "b_client_request_talker": 0
        }
    }

    def __init__(self):
        self.checkServer(ts3lib.getCurrentServerConnectionHandlerID())
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self): pass

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID != 0 or atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL: return
        print("schids:",self.schids); print("suid:",self.suid); print("mychan:",self.mychan); print("supchan:",self.supchan); print("myuid:",self.myuid)
        cid = self.getChannel(schid)
        if not cid: return
        ts3lib.requestChannelDelete(schid, cid, True)
        self.supchan = 0

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: self.schid = schid; QTimer.singleShot(10000, self.checkServer)
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if schid in self.schids: self.schids.remove(schid)
            if len(self.schids) < 1 and self.supchan:
                with ts3.query.TS3ServerConnection("51.255.133.6", 1976) as ts3conn:
                    err = ts3conn.query("login", client_login_name="bl", client_login_password="") # TODO: REMOVE BEFORE COMMIT
                    print("login:",err.all())
                    err = ts3conn.query("use", port=9987)
                    print("use:",err.all())
                    err = ts3conn.query("clientupdate", client_nickname="Bluscream")
                    print("clientupdate client_nickname=Bluscream:",err.all())
                    err = ts3conn.query("channeldelete", cid=self.supchan, force=1)
                    print("channeldelete cid=%s force=1: %s"%(self.supchan, err.all()))
                    self.supchan = 0

    def checkServer(self, schid=None):
        if not schid: schid = self.schid
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        (err, ownuid) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        if ownuid != self.myuid: return
        self.toggleChannel(schid)
        self.schids.append(schid)

    def toggleChannel(self, schid):
        supchan = self.getChannel(schid)
        if supchan:
            self.supchan = supchan
            self.getChannel(schid)
        else: self.createChannel(schid)

    def getChannel(self, schid):
        (err, cids) = ts3lib.getChannelList(schid)
        for cid in cids:
            (err, perm) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PERMANENT)
            if not perm: continue
            (err, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
            if not self.supchan_props["name"] in name: continue
            (err, parent) = ts3lib.getParentChannelOfChannel(schid, cid)
            if not parent == self.mychan: continue
            return cid
        return 0

    def createChannel(self, schid):
        ts3lib.setChannelVariableAsString(schid, 0, ts3defines.ChannelProperties.CHANNEL_NAME, self.supchan_props["name"])
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, self.supchan_props["maxclients"])
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_CODEC, self.supchan_props["codec"])
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_CODEC_QUALITY, self.supchan_props["codec_quality"])
        ts3lib.setChannelVariableAsString(schid, 0, ts3defines.ChannelProperties.CHANNEL_DESCRIPTION, self.supchan_props["description"])
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_FLAG_PERMANENT, 1)
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_MAXCLIENTS_UNLIMITED, 0)
        ts3lib.flushChannelCreation(schid, self.mychan)
        self.waitforchannel = True

    def checkChannel(self, schid):
        (err, clients) = ts3lib.getChannelClientList(schid, self.supchan); clients = len(clients)
        (err, maxclients) = ts3lib.getChannelVariable(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        if clients < maxclients:
            ts3lib.setChannelVariableAsString(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_NAME, "{} [OFFEN]".format(self.supchan_props["name"]))
        elif clients >= maxclients:
            ts3lib.setChannelVariableAsString(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_NAME, "{} [BESETZT]".format(self.supchan_props["name"]))
        else: return
        ts3lib.flushChannelUpdates(schid, self.supchan)

    def onNewChannelCreatedEvent(self, schid, cid, channelParentID, invokerID, invokerName, invokerUniqueIdentifier):
        if not self.waitforchannel: return
        if not channelParentID == self.mychan: return
        self.waitforchannel = False
        self.supchan = cid
        for perm in self.supchan_props["permissions"]:
            (err, id) = ts3lib.getPermissionIDByName(schid, perm)
            ts3lib.requestChannelAddPerm(schid, cid, [id], [self.supchan_props["permissions"][perm]])
        self.checkChannel(schid)

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        if schid != self.schids[0]: return
        if not self.supchan in [newChannelID, oldChannelID]: return
        (err, ownID) = ts3lib.getClientID(schid)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        (err, clients) = ts3lib.getChannelClientList(schid, self.mychan); clients = len(clients)
        if ownCID == self.mychan and clients == 1:
            ts3lib.requestClientMove(schid, clid, self.mychan, "")
        else: self.checkChannel(schid)

    def onClientMoveMovedEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
        if schid != self.schids[0]: return
        if self.supchan in [newChannelID, oldChannelID]: self.checkChannel(schid)

    def onClientKickFromChannelEvent(self, schid, clid, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        if schid != self.schids[0]: return
        if self.supchan == oldChannelID: self.checkChannel(schid)

    def onClientKickFromServerEvent(self, schid, clid, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        if schid != self.schids[0]: return
        if self.supchan == oldChannelID: self.checkChannel(schid)

    def onClientBanFromServerEvent(self, schid, clid, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, time, kickMessage):
        if schid != self.schids[0]: return
        if self.supchan == oldChannelID: self.checkChannel(schid)