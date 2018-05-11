import ts3defines, ts3lib, pytson
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from bluscream import saveCfg, loadCfg, timestamp, intList, getScriptPath
from configparser import ConfigParser

class quickMod(ts3plugin):
    path = getScriptPath(__name__)
    name = "Quick Moderation"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Allows you to set hotkeys for quick moderation (ban/restrict/remove tp)"
    offersConfigure = False
    commandKeyword = "qm"
    infoTitle = None
    menuItems = []
    hotkeys = [
        ("restrict_last_joined_server", "Restrict the last user that joined your server"),
        ("restrict_last_joined_channel", "Restrict the last user that joined your channel"),
        ("ban_last_joined_server", "Bans the last user that joined your server"),
        ("ban_last_joined_channel", "Bans the last user that joined your channel"),
        ("revoke_last_talk_power", "Revoke talk power from the last user that got TP in your channel"),
        ("restrict_last_joined_channel_from_local_channels", "Give the last user that joined your channel a cgid and sgid in certain channels"),
        ("last_joined_channel_to_customBan", "Gives the last user that joined your channel to the customBan dialog"),
        ("last_joined_server_to_customBan", "Gives the last user that joined your server to the customBan dialog"),
    ]
    last_joined_server = 0
    last_joined_channel = 0
    last_talk_power = 0
    requested = 0
    requestedIP = 0
    retcode = ""
    customBan = None
    ini = "%s/config.ini" % path
    cfg = ConfigParser()
    cfg["ban"] = { "duration": "2678400", "reason": "Ban Evading / Bannumgehung", "poke": "[color=red][b]You we're banned from the server!" }
    cfg["restrict"] = { "sgids": "", "reason": "Ban Evading / Bannumgehung", "poke": "" }
    cfg["restrict local"] = { "cids": "", "sgids": "", "cgid": "", "poke": "" }
    moveBeforeBan = 26

    def __init__(self):
        loadCfg(self.ini, self.cfg)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def stop(self):
        pass # saveCfg(self.ini, self.cfg)

    def processCommand(self, schid, keyword): self.onHotkeyOrCommandEvent(keyword, schid)

    def onHotkeyEvent(self, keyword): self.onHotkeyOrCommandEvent(keyword)

    def onHotkeyOrCommandEvent(self, keyword, schid=0):
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        if keyword == "restrict_last_joined_server":
            self.requested = self.last_joined_server
            msg = self.cfg.get("restrict", "poke")
            if msg: ts3lib.requestClientPoke(schid, self.requested, msg)
            ts3lib.requestClientVariables(schid, self.last_joined_server)
            # self.restrictClient(schid, self.last_joined_server)
        elif keyword == "restrict_last_joined_channel":
            self.requested = self.last_joined_channel
            msg = self.cfg.get("restrict", "poke")
            if msg: ts3lib.requestClientPoke(schid, self.requested, msg)
            ts3lib.requestClientVariables(schid, self.last_joined_channel)
            # self.restrictClient(schid, self.last_joined_channel)
        elif keyword == "ban_last_joined_server":
            msg = self.cfg.get("ban", "poke")
            if msg: ts3lib.requestClientPoke(schid, self.last_joined_server, msg)
            self.banClient(schid, self.last_joined_server)
        elif keyword == "ban_last_joined_channel":
            msg = self.cfg.get("ban", "poke")
            if msg: ts3lib.requestClientPoke(schid, self.last_joined_channel, msg)
            self.banClient(schid, self.last_joined_channel)
        elif keyword == "revoke_last_talk_power_channel":
            self.revokeTalkPower(schid, self.last_talk_power)
        elif keyword == "restrict_last_joined_channel_from_local_channels":
            self.restrictForeigners(schid, self.last_joined_channel)
        elif keyword == "last_joined_channel_to_customBan":
            self.toCustomBan(schid, self.last_joined_channel)
        elif keyword == "last_joined_server_to_customBan":
            self.toCustomBan(schid, self.last_joined_server)

    def toCustomBan(self, schid, clid):
        active = PluginHost.active
        if not "Custom Ban" in active: return
        active["Custom Ban"].onMenuItemEvent(schid, ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, clid)

    def banClient(self, schid, clid):
        (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        (err, ip) = ts3lib.getConnectionVariable(schid, clid, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
        if self.moveBeforeBan: ts3lib.requestClientMove(schid, clid, self.moveBeforeBan, "")
        if not ip: self.requestedIP = clid; ts3lib.requestConnectionInfo(schid, clid)
        else: self.banIP(schid, ip); self.banUID(schid, uid)

    def onUpdateClientEvent(self, schid, clid, invokerID, invokerName, invokerUniqueIdentifier):
        if clid == self.requestedIP:
            self.requestedIP = 0
            (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            (err, ip) = ts3lib.getConnectionVariable(schid, clid, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
            self.banIP(schid, ip)
            self.banUID(schid, uid)
            return
        (err, ownID) = ts3lib.getClientID(schid)
        (err, cid) = ts3lib.getChannelOfClient(schid, clid)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        (err, talker) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
        if cid == ownCID and talker: self.last_talk_power = clid
        if clid == self.requested:
            self.requested = 0
            if talker == 1: self.revokeTalkPower(schid, clid, True)
            # else: self.revokeTalkPower(schid, clid, False)
            (err, cldbid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
            (err, sgids) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
            loc_sgids = intList(self.cfg.get("restrict", "sgids"))
            if set(loc_sgids).issubset(sgids):
                for sgid in loc_sgids: ts3lib.requestServerGroupDelClient(schid, sgid, cldbid)
            else:
                for sgid in loc_sgids: ts3lib.requestServerGroupAddClient(schid, sgid, cldbid)

    def revokeTalkPower(self, schid, clid, revoke=True):
        self.retcode = ts3lib.createReturnCode()
        ts3lib.requestClientSetIsTalker(schid, clid, revoke, self.retcode)

    def restrictForeigners(self, schid, clid):
        (err, cldbid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        (err, sgids) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        loc_sgids = intList(self.cfg.get("restrict local", "sgids"))
        loc_cids = intList(self.cfg.get("restrict local", "cids"))
        if sgids and set(loc_sgids).issubset(sgids):
            for sgid in loc_sgids: ts3lib.requestServerGroupDelClient(schid, sgid, cldbid)
            (err, dcgid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
            ts3lib.requestSetClientChannelGroup(schid, [dcgid]*len(loc_cids), loc_cids, [cldbid]*len(loc_cids))
            return
        for sgid in loc_sgids: ts3lib.requestServerGroupAddClient(schid, sgid, cldbid)
        ts3lib.requestSetClientChannelGroup(schid, [self.cfg.getint("restrict local", "cgid")]*len(loc_cids), loc_cids, [cldbid]*len(loc_cids))
        msg = self.cfg.get("restrict local", "poke")
        if msg: ts3lib.requestClientPoke(schid, self.last_joined_channel, msg)
        # ts3lib.requestClientKickFromChannel(schid, clid, msg)

    def banReason(self):
        reason = self.cfg.get("ban", "reason")
        if reason[0].isdigit():
            reason = "§" + reason
        return reason

    def banUID(self, schid, uid):
        ts3lib.banadd(schid, "", "", uid, self.cfg.getint("ban", "duration"), self.banReason())
        print("banned uid",uid)

    def banIP(self, schid, ip):
        if not ip: return
        active = PluginHost.active
        if "Custom Ban" in active:
            whitelist = active["Custom Ban"].whitelist
            if len(whitelist) > 1:
                if ip in whitelist: ts3lib.printMessageToCurrentTab("{}: [color=red]Not banning whitelisted IP [b]{}".format(self.name, ip)); return
            else: ts3lib.printMessageToCurrentTab("{}: \"Custom Ban\"'s IP Whitelist faulty, please check!".format(self.name)); return
        ts3lib.banadd(schid, ip, "", "", self.cfg.getint("ban", "duration"), self.banReason())
        print("banned ip",ip)

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        if schid != ts3lib.getCurrentServerConnectionHandlerID(): return
        (err, ownID) = ts3lib.getClientID(schid)
        if clid == ownID: return
        if oldChannelID == 0: self.last_joined_server = clid
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if newChannelID == ownCID: self.last_joined_channel = clid

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode == self.retcode: return True
