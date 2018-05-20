import ts3lib, ts3defines, datetime, ts3
from configparser import ConfigParser
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from bluscream import timestamp, getScriptPath, loadCfg

class mySupport(ts3plugin):
    path = getScriptPath(__name__)
    name = "my Support"
    apiVersion = 22
    requestAutoload = False
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
    supchan = 0
    cfg = ConfigParser()
    # cfg.optionxform = str
    cfg["general"] = {
        "suid": "9lBVIDJRSSgAGy+cWJgNlUQRd64=",
        "myuid": "e3dvocUFTE1UWIvtW8qzulnWErI=",
        "mychan": 0
    }
    chan = ConfigParser()
    chan["props"] = {
        "name": "Waiting For Support",
        "maxclients": 1,
        "codec": ts3defines.CodecType.CODEC_SPEEX_NARROWBAND,
        "codec_quality": 0,
        "name open": "Waiting For Support [OPEN]",
        "name closed": "Waiting For Support [CLOSED]",
        "name in use": "Waiting For Support [IN USE]"
    }
    chan["permissions"] = {
        "i_channel_needed_modify_power": 75,
        "i_channel_needed_permission_modify_power": 75,
        "i_channel_needed_delete_power": 75,
        "i_channel_needed_subscribe_power": 75,
        "b_client_request_talker": 0
    }

    def __init__(self):
        loadCfg(self.path+"/config.ini", self.cfg)
        loadCfg(self.path+"/channel.ini", self.chan)
        self.checkServer(ts3lib.getCurrentServerConnectionHandlerID())
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self): pass

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID != 0 or atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL: return
        cid = self.getChannel(schid)
        if not cid: return
        ts3lib.requestChannelDelete(schid, cid, True)
        self.supchan = 0

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.schid = schid
            QTimer.singleShot(10000, self.checkServer)
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab(self.name+"> Checking for channel in 10 seconds")
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if schid in self.schids: self.schids.remove(schid)
            if len(self.schids) < 1 and self.supchan:
                with ts3.query.TS3ServerConnection(self.cfg.get("serverquery","host"), self.cfg.getint("serverquery","qport")) as ts3conn:
                    err = ts3conn.query("login", client_login_name=self.cfg.get("serverquery","name"), client_login_password=self.cfg.get("serverquery","pw"))
                    print("[OUT] login client_login_name client_login_password [IN]",err.all())
                    err = ts3conn.query("use", port=self.cfg.getint("serverquery","port"))
                    print("[OUT] use port [IN]",err.all())
                    err = ts3conn.query("clientupdate", client_nickname=self.cfg.get("serverquery","nick"))
                    print("[OUT] clientupdate client_nickname [IN]",err.all())
                    err = ts3conn.query("channeldelete", cid=self.supchan, force=1)
                    print("[OUT] channeldelete cid=%s force=1 [IN] %s"%(self.supchan, err.all()))
                    self.supchan = 0

    def checkServer(self, schid=None):
        if not schid: schid = self.schid
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        (err, ownuid) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if PluginHost.cfg.getboolean("general", "verbose"):
            ts3lib.printMessageToCurrentTab(self.name+"> Checking for channel....")
            print("suid:",suid,self.cfg.get("general","suid"))
            print("myuid",ownuid,self.cfg.get("general","myuid"))
        if suid != self.cfg.get("general","suid"): return
        if ownuid != self.cfg.get("general","myuid"): return
        self.toggleChannel(schid)
        self.schids.append(schid)

    def toggleChannel(self, schid):
        supchan = self.getChannel(schid)
        if supchan:
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Channel #%s does exist"%supchan)
            self.supchan = supchan
            self.getChannel(schid)
        else:
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Channel does not exist, creating...")
            self.createChannel(schid)

    def getChannel(self, schid):
        (err, cids) = ts3lib.getChannelList(schid)
        for cid in cids:
            (err, perm) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PERMANENT)
            if not perm: continue
            (err, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
            if not self.chan.get("props", "name") in name: continue
            (err, parent) = ts3lib.getParentChannelOfChannel(schid, cid)
            if not parent == self.cfg.getint("general","mychan"): continue
            return cid
        return 0

    def createChannel(self, schid):
        ts3lib.setChannelVariableAsString(schid, 0, ts3defines.ChannelProperties.CHANNEL_NAME, self.chan.get("props", "name"))
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, self.chan.getint("props", "maxclients"))
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_CODEC, self.chan.getint("props", "codec"))
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_CODEC_QUALITY, self.chan.getint("props", "codec_quality"))
        ts3lib.setChannelVariableAsString(schid, 0, ts3defines.ChannelProperties.CHANNEL_DESCRIPTION, self.chan.get("props", "description"))
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_FLAG_PERMANENT, 1)
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_MAXCLIENTS_UNLIMITED, 0)
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER, 1337)
        ts3lib.flushChannelCreation(schid, self.cfg.getint("general","mychan"))
        self.waitforchannel = True

    def checkChannel(self, schid):
        (err, clients) = ts3lib.getChannelClientList(schid, self.supchan); clients = len(clients)
        (err, maxclients) = ts3lib.getChannelVariable(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        if clients < maxclients:
            ts3lib.setChannelVariableAsString(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_NAME,self.chan.get("props", "name open"))
        elif clients >= maxclients:
            ts3lib.setChannelVariableAsString(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_NAME, self.chan.get("props", "name in use"))
        else: return
        ts3lib.flushChannelUpdates(schid, self.supchan)

    def onNewChannelCreatedEvent(self, schid, cid, channelParentID, invokerID, invokerName, invokerUniqueIdentifier):
        if not self.waitforchannel: return
        if not channelParentID == self.cfg.getint("general","mychan"): return
        self.waitforchannel = False
        self.supchan = cid
        for (key, val) in self.chan.items("permissions"):
            (err, id) = ts3lib.getPermissionIDByName(schid, key)
            ts3lib.requestChannelAddPerm(schid, cid, [id], [int(val)])
        self.checkChannel(schid)

    def onClientSelfVariableUpdateEvent(self, schid, flag, oldValue, newValue) :
        if not self.schids or len(self.schids) < 1 or schid != self.schids[0]: return
        if flag != ts3defines.ClientPropertiesRare.CLIENT_AWAY: return
        newValue = int(newValue)
        if newValue == ts3defines.AwayStatus.AWAY_ZZZ:
            ts3lib.setChannelVariableAsInt(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, 0)
            ts3lib.setChannelVariableAsString(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_NAME, self.chan.get("props", "name closed"))
            ts3lib.flushChannelUpdates(schid, self.supchan)
        elif newValue == ts3defines.AwayStatus.AWAY_NONE:
            ts3lib.setChannelVariableAsInt(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, self.chan.getint("props", "maxclients"))
            ts3lib.setChannelVariableAsString(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_NAME, self.chan.get("props", "name open"))
            ts3lib.flushChannelUpdates(schid, self.supchan)
            # self.checkChannel(schid)

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.schids or len(self.schids) < 1 or schid != self.schids[0]: return
        if not self.supchan in [newChannelID, oldChannelID]: return
        (err, ownID) = ts3lib.getClientID(schid)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        mychan = self.cfg.getint("general","mychan")
        (err, clients) = ts3lib.getChannelClientList(schid, mychan); clients = len(clients)
        if ownCID == mychan and clients == 1:
            ts3lib.requestClientMove(schid, clid, mychan, "")
        else: self.checkChannel(schid)

    def onClientMoveMovedEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
        if not self.schids or len(self.schids) < 1 or schid != self.schids[0]: return
        if self.supchan in [newChannelID, oldChannelID]: self.checkChannel(schid)

    def onClientKickFromChannelEvent(self, schid, clid, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        if not self.schids or len(self.schids) < 1 or schid != self.schids[0]: return
        if self.supchan == oldChannelID: self.checkChannel(schid)

    def onClientKickFromServerEvent(self, schid, clid, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        if not self.schids or len(self.schids) < 1 or schid != self.schids[0]: return
        if self.supchan == oldChannelID: self.checkChannel(schid)

    def onClientBanFromServerEvent(self, schid, clid, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, time, kickMessage):
        if not self.schids or len(self.schids) < 1 or schid != self.schids[0]: return
        if self.supchan == oldChannelID: self.checkChannel(schid)