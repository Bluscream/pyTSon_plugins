import ts3defines, ts3lib, pytson
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from bluscream import saveCfg, loadCfg, timestamp, intList, getScriptPath, widget, getIDByName, getChannelPassword
from ts3enums import ServerTreeItemType
from configparser import ConfigParser
from PythonQt.Qt import QApplication

class quickMod(ts3plugin):
    path = getScriptPath(__name__)
    name = "Quick Moderation"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
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
        ("join_selected_channel_pw", "Joins the selected channel (Bypasses passwords)"),
        ("rejoin_last_channel_pw", "Rejoins the last channel you left (Bypasses passwords)")
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
    cfg["ban"] = { "duration": "2678400", "reason": "Ban Evading / Bannumgehung", "poke": "[color=red][b]You were banned from the server!", "name duration ": 120 }
    cfg["restrict"] = { "sgids": "", "poke": "" }
    cfg["restrict local"] = { "cids": "", "sgids": "", "cgid": "", "poke": "" }
    moveBeforeBan = 277
    sgids = [129,127,126,124]
    lastchans = {}

    def __init__(self):
        self.app = QApplication.instance()
        loadCfg(self.ini, self.cfg)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def stop(self):
        pass # saveCfg(self.ini, self.cfg)

    def processCommand(self, schid, keyword): self.onHotkeyOrCommandEvent(keyword, schid)
    def onHotkeyEvent(self, keyword): self.onHotkeyOrCommandEvent(keyword)
    def onHotkeyOrCommandEvent(self, keyword, schid=0):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
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
        elif keyword == "join_selected_channel_pw":
            window = self.app.activeWindow()
            if window is None or not window.className() == "MainWindow": return
            selected = widget("ServerTreeView", self.app).currentIndex()
            if not selected: return
            name = selected.data()
            item = getIDByName(name, schid)
            if item[1] != ServerTreeItemType.CHANNEL: return
            (err, clid) = ts3lib.getClientID(schid)
            (err, cid) = ts3lib.getChannelOfClient(schid, clid)
            if cid == item[0]: return
            pw = getChannelPassword(schid, item[0], calculate=True)
            if not pw: return
            # ts3lib.printMessageToCurrentTab("{} > Joining {} (pw: {})".format(self.name, name, pw))
            ts3lib.requestClientMove(schid, clid, item[0], pw)
        elif keyword == "rejoin_last_channel_pw":
            (err, clid) = ts3lib.getClientID(schid)
            (err, cid) = ts3lib.getChannelOfClient(schid, clid)
            tcid = self.lastchans[schid]
            if cid == tcid: return
            pw = getChannelPassword(schid, tcid, calculate=True)
            # (err, name) = ts3lib.getChannelVariable(schid, tcid, ts3defines.ChannelProperties.CHANNEL_NAME)
            # ts3lib.printMessageToCurrentTab("{} > Rejoining {} (pw: {})".format(self.name, name, pw))
            ts3lib.requestClientMove(schid, clid, tcid, pw if pw else "123")

    def toCustomBan(self, schid, clid):
        active = PluginHost.active
        if not "Custom Ban" in active: return
        active["Custom Ban"].onMenuItemEvent(schid, ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, clid)

    def banClient(self, schid, clid):
        (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        (err, ip) = ts3lib.getConnectionVariable(schid, clid, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
        if self.moveBeforeBan: ts3lib.requestClientMove(schid, clid, self.moveBeforeBan, "")
        if not ip:
            self.requestedIP = clid
            ts3lib.requestConnectionInfo(schid, clid)
        else:
            self.banIP(schid, ip)
            self.banUID(schid, uid)
            if self.cfg.getint("ban", "duration") != 0:
                (err, name) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
                self.banName(schid, clid, name)

    def onConnectionInfoEvent(self, schid, clid):
        if clid == self.requestedIP:
            self.requestedIP = 0
            (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            (err, ip) = ts3lib.getConnectionVariable(schid, clid, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
            self.banIP(schid, ip)
            self.banUID(schid, uid)
            if self.cfg.getint("ban", "duration") != 0:
                (err, name) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
                self.banName(schid, clid, name)

    def onUpdateClientEvent(self, schid, clid, invokerID, invokerName, invokerUniqueIdentifier):
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

    def banIP(self, schid, ip):
        if not ip: return
        active = PluginHost.active
        if "Custom Ban" in active:
            whitelist = active["Custom Ban"].whitelist
            if len(whitelist) > 1:
                if ip in whitelist: ts3lib.printMessageToCurrentTab("{}: [color=red]Not banning whitelisted IP [b]{}".format(self.name, ip)); return
            else: ts3lib.printMessageToCurrentTab("{}: \"Custom Ban\"'s IP Whitelist faulty, please check!".format(self.name)); return
        ts3lib.banadd(schid, ip, "", "", self.cfg.getint("ban", "duration"), self.banReason())

    def banName(self, schid, target, name):
        name_in_use = False
        (err, clids) = ts3lib.getClientList(schid)
        for clid in clids:
            if clid == target: continue
            (err, _name) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
            if name in _name: name_in_use = True
        if not name_in_use: name = ".*{}.*".format(name)
        print("inuse:", name_in_use, "name:",name)
        ts3lib.banadd(schid, "", name, "", self.cfg.getint("ban", "name duration"), self.banReason())

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        (err, ownID) = ts3lib.getClientID(schid)
        if clid == ownID: self.lastchans[schid] = oldChannelID
        if schid != ts3lib.getCurrentServerConnectionHandlerID(): return
        if clid == ownID: return
        (err, sgids) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        if sgids is not None:
            sgids = intList(sgids)
            if not any(x in sgids for x in self.sgids): return
        if oldChannelID == 0: self.last_joined_server = clid
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if newChannelID == ownCID: self.last_joined_channel = clid

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode == self.retcode: return True
