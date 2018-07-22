import ts3lib, ts3defines, datetime, pytson
from configparser import ConfigParser
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from PythonQt.QtGui import QMessageBox
from bluscream import timestamp, getScriptPath, loadCfg
from io import StringIO

class mySupport(ts3plugin):
    path = getScriptPath(__name__)
    name = "my Support"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "ms"
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, "")]
    hotkeys = [("move_first_from_waiting_room", "Move the first client from your waiting room to your room")]
    schid = 1
    schids = []
    waitforchannel = False
    supchan = 0
    perm = (0,"","")
    cfg = ConfigParser()
    # cfg.optionxform = str
    cfg["general"] = {
        "servername": "Mein Server",
        "myuid": "e3dvocUFTE1UWIvtW8qzulnWErI=",
        "mychan": "Vater Channel,Mein Channel"
    }
    chan = ConfigParser()
    chan["props"] = {
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
        with open(self.path+"/description.txt", 'r') as myfile: self.description = myfile.read()
        self.checkServer(ts3lib.getCurrentServerConnectionHandlerID())
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self): pass

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID != 0 or atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL: return
        cid = self.getChannel(schid)
        if not cid: return
        ts3lib.requestChannelDelete(schid, cid, True)
        self.supchan = 0

    def processCommand(self, schid, keyword): self.onHotkeyOrCommandEvent(keyword, schid)

    def onHotkeyEvent(self, keyword): self.onHotkeyOrCommandEvent(keyword)

    def onHotkeyOrCommandEvent(self, keyword, schid=0):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        if not self.schids or len(self.schids) < 1 or schid != self.schids[0] or not self.supchan: return
        if keyword == "move_first_from_waiting_room":
            (err, clids) = ts3lib.getChannelClientList(schid, self.supchan)
            (err, ownID) = ts3lib.getClientID(schid)
            (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
            ts3lib.requestClientMove(schid, clids[0], ownCID, "")

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.schid = schid
            QTimer.singleShot(10000, self.checkServer)
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab(self.name+"> Checking for channel in 10 seconds")
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if schid in self.schids: self.schids.remove(schid)
            if len(self.schids) < 1 and self.supchan:
                self.deleteChan()

    def deleteChan(self):
        try: import ts3
        except ImportError:
            from devtools import PluginInstaller
            PluginInstaller().installPackages(['ts3'])
            import ts3
        host=self.cfg.get("serverquery","host")
        qport=self.cfg.getint("serverquery","qport")
        client_login_name=self.cfg.get("serverquery","name")
        client_login_password=self.cfg.get("serverquery","pw")
        port=self.cfg.getint("serverquery","port")
        client_nickname=self.cfg.get("serverquery","nick")
        if hasattr(ts3.query, "TS3ServerConnection"):
            with ts3.query.TS3ServerConnection(host, qport) as ts3conn:
                ts3conn.query("login", client_login_name=client_login_name, client_login_password=client_login_password).fetch()
                ts3conn.query("use", port=port).fetch()
                ts3conn.query("clientupdate", client_nickname=client_nickname).fetch()
                ts3conn.query("channeldelete", cid=self.supchan, force=1).fetch()
        else:
            with ts3.query.TS3Connection(host, qport) as ts3conn:
                ts3conn.login(client_login_name=client_login_name, client_login_password=client_login_password)
                ts3conn.use(port=port)
                ts3conn.clientupdate(client_nickname=client_nickname)
                ts3conn.channeldelete(cid=self.supchan, force=True)
        self.supchan = 0

    def checkServer(self, schid=None):
        if not schid: schid = self.schid
        (err, servername) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
        (err, ownuid) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if PluginHost.cfg.getboolean("general", "verbose"):
            ts3lib.printMessageToCurrentTab(self.name+"> Checking for channel....")
            print("servername:", servername, "cfg:",self.cfg.get("general","servername"), servername == self.cfg.get("general","servername"))
            print("myuid",ownuid,self.cfg.get("general","myuid"), ownuid == self.cfg.get("general","myuid"))
        if servername != self.cfg.get("general","servername"): return
        if ownuid != self.cfg.get("general","myuid"): return
        mychan = self.cfg.get("general", "mychan").split(",")
        mycid = ts3lib.getChannelIDFromChannelNames(schid, mychan)
        self.schids.append({schid: mycid})
        self.toggleChannel(schid)

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
            (err, perm) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_SEMI_PERMANENT)
            if not perm: continue
            (err, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
            if not self.chan.get("props", "name") in name: continue
            (err, parent) = ts3lib.getParentChannelOfChannel(schid, cid)
            if not parent == self.schids[schid]: continue
            return cid
        return 0

    def createChannel(self, schid):
        ts3lib.setChannelVariableAsString(schid, 0, ts3defines.ChannelProperties.CHANNEL_NAME, self.chan.get("props", "name open"))
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, self.chan.getint("props", "maxclients"))
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_CODEC, self.chan.getint("props", "codec"))
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_CODEC_QUALITY, self.chan.getint("props", "codec_quality"))
        ts3lib.setChannelVariableAsString(schid, 0, ts3defines.ChannelProperties.CHANNEL_DESCRIPTION, self.description)
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelProperties.CHANNEL_FLAG_SEMI_PERMANENT, 1)
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_MAXCLIENTS_UNLIMITED, 0)
        ts3lib.setChannelVariableAsInt(schid, 0, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER, 1337)
        print(self.schids)
        print(self.schids[schid])
        return
        ts3lib.flushChannelCreation(schid, self.schids[schid])
        self.waitforchannel = True

    def onNewChannelCreatedEvent(self, schid, cid, channelParentID, invokerID, invokerName, invokerUniqueIdentifier):
        if not self.waitforchannel: return
        mycid = ts3lib.getChannelIDFromChannelNames(schid, self.cfg.get("general", "mychan").split(","))
        if not channelParentID == mycid: return
        self.waitforchannel = False
        self.supchan = cid
        for (key, val) in self.chan.items("permissions"):
            (err, id) = ts3lib.getPermissionIDByName(schid, key)
            self.perm = (id, key, ts3lib.createReturnCode())
            ts3lib.requestChannelAddPerm(schid, cid, [id], [int(val)])
        # self.checkChannel(schid)

    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        print(returnCode, self.perm[2])
        if returnCode != self.perm[2]: return
        perm = self.perm
        ts3lib.printMessage(schid, "{}: Error setting permission [{}] #{} ({}): {} ({})".format(self.name, failedPermissionID, perm[0],perm[1],error,errorMessage), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
        self.perm = (0,"","")

    def checkChannel(self, schid):
        (err, clients) = ts3lib.getChannelClientList(schid, self.supchan); clients = len(clients)
        (err, maxclients) = ts3lib.getChannelVariable(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        if clients < maxclients:
            ts3lib.setChannelVariableAsString(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_NAME,self.chan.get("props", "name open"))
        elif clients >= maxclients:
            ts3lib.setChannelVariableAsString(schid, self.supchan, ts3defines.ChannelProperties.CHANNEL_NAME, self.chan.get("props", "name in use"))
        else: return
        ts3lib.flushChannelUpdates(schid, self.supchan)

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
        mycid = ts3lib.getChannelIDFromChannelNames(schid, self.cfg.get("general", "mychan").split(","))
        (err, clients) = ts3lib.getChannelClientList(schid, mycid); clients = len(clients)
        if ownCID == mycid and clients == 1 and newChannelID == self.supchan:
            ts3lib.requestClientMove(schid, clid, mycid, "")
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