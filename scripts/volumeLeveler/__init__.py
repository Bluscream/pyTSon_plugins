import ts3lib, ts3defines
from datetime import datetime
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from ts3Ext import ts3SessionHost, logLevel
from bluscream import timestamp, sendCommand, getAddons, inputInt, calculateInterval, AntiFloodPoints, intList, parseTime, getContactStatus, ContactStatus, varname

class Mode(object):
    REVOKE_TALK_POWER = 0
    CHANNEL_BAN = 1

def parseMessage(logMessage):
    log = intList(logMessage, ";")
    return log[0], log[1]

class volumeLeveler(ts3plugin):
    name = "Volume Leveler"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "( .) ( .)"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    clients = {}
    maxlevel = 20000
    maxviolations = 15
    mode = Mode.REVOKE_TALK_POWER
    guiLogLvl = logLevel.ALL
    ts3host = None
    banned_names = ["BAN", "NOT WELCOME"]
    mod_names = ["MOD", "OPERATOR"]
    admin_names = ["ADMIN"]

    def __init__(self):
        if "aaa_ts3Ext" in PluginHost.active: self.ts3host = PluginHost.active["aaa_ts3Ext"].ts3host
        else: self.ts3host = ts3SessionHost(self)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onUserLoggingMessageEvent(self, logMessage, logLevel, logChannel, schid, logTime, completeLogString):
        if logLevel != ts3defines.LogLevel.LogLevel_DEBUG: return
        if schid != ts3lib.getCurrentServerConnectionHandlerID(): return
        if logChannel != "VolumeLeveler": return
        clid, level = parseMessage(logMessage)
        if not clid in self.clients: return
        # date = parseTime(logTime)
        if self.clients[clid] > self.maxviolations:
            self.clients[clid] = 0
            groups = self.ts3host.getServer(schid)._ts3ChannelGroups
            (err, country) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_COUNTRY)
            err = 0
            msg = "[color=red]You exceeded the volume limit {violations} times, your talk power has been revoked!"
            if country in ["DE", "AT", "CH"]: msg = "[color=red]Du hast {violations} mal das Lautstaerkelimit von {limit} ueberschritten, deine Talk Power wurde entzogen!"
            if self.mode == Mode.REVOKE_TALK_POWER:
                err = ts3lib.requestClientSetIsTalker(schid, clid, False)
            elif self.mode == Mode.CHANNEL_BAN:
                (err, cid) = ts3lib.getChannelOfClient(schid, clid)
                (err, dbid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                err = ts3lib.requestSetClientChannelGroup(schid, [self.bancgid], [cid], [dbid])
                err = ts3lib.requestClientSetIsTalker(schid, clid, False)
            if err != ts3defines.ERROR_ok: return
            ts3lib.requestSendPrivateTextMsg(schid, msg.replace("{violations}",str(self.maxviolations)).replace("{limit}",str(self.maxlevel)), clid)
            return
        if level > self.maxlevel:
            self.clients[clid] += 1
            print(clid, level, self.clients[clid])

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        (err, ownID) = ts3lib.getClientID(schid)
        if clid == ownID:
            self.clients = {}
            return #(err, clids) = ts3lib.getChannelClientList(schid, newChannelID)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if not ownCID in [newChannelID, oldChannelID]: return
        (err, owncgid) = ts3lib.getClientVariable(schid, ownID, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
        if not owncgid in [10,11]: return
        (err, tp) = ts3lib.getChannelVariable(schid, ownCID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        if not tp or tp < 1 or tp == "-1": self.mode = Mode.CHANNEL_BAN
        else: self.mode = Mode.REVOKE_TALK_POWER
        """
        (err, acgid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_ADMIN_GROUP)
        (err, ownCGID) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
        if ownCGID != acgid: return
        """
        (err, perm) = ts3lib.getClientNeededPermission(schid, "b_client_set_flag_talker")
        if not perm: return
        if newChannelID == ownCID:
            (err, cgid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
            (err, dcgid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
            if cgid != dcgid: return
            (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            status = getContactStatus(uid)
            if status == ContactStatus.FRIEND: return
            self.clients[clid] = 0
        elif oldChannelID == ownCID:
            if clid in self.clients: del self.clients[clid]

    def onUpdateChannelEditedEvent(self, schid, cid, clid, invokerName, invokerUniqueIdentifier):
        (err, ownID) = ts3lib.getClientID(schid)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if cid != ownCID: return
        (err, tp) = ts3lib.getChannelVariable(schid, ownCID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        if not tp or tp < 1 or tp == "-1": self.mode = Mode.CHANNEL_BAN
        else: self.mode = Mode.REVOKE_TALK_POWER

"""
    fullchannel: 0 newChannelID: 0
Error calling method onClientMoveEvent of plugin Channel Queue: Traceback (most recent call last):
  File "C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/scripts\pluginhost.py", line 394, in invokePlugins
    ret.append(meth(*args))
  File "C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/scripts\joinChannel\__init__.py", line 77, in onClientMoveEvent
    ts3lib.setChannelVariableAsInt(schid, newChannelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, maxclients - 1)
TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'
"""