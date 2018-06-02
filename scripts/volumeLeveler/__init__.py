import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from PythonQt.QtCore import QTimer
from bluscream import timestamp, intList, getContactStatus, ContactStatus

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
    ts3host = None
    tabs = {}
    mode = Mode.REVOKE_TALK_POWER
    maxlevel = 30000
    maxviolations = 15

    def __init__(self):
        if "aaa_ts3Ext" in PluginHost.active:
            ts3ext = PluginHost.active["aaa_ts3Ext"]
            self.ts3host = ts3ext.ts3host
            self.tabs = ts3ext.tabs
        else: QTimer.singleShot(500, self.__init__)
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
            client = self.ts3host.getUser(schid, clid)
            if not client.server.me.getChannelGroupId() in [self.tabs[schid]["channelModGroup"], client.server.defaultChannelAdminGroup]:
                client.mute()
                return
            (err, country) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_COUNTRY)
            msg = "[color=red]You exceeded the volume limit {violations} times, your talk power has been revoked!"
            if country in ["DE", "AT", "CH"]: msg = "[color=red]Du hast {violations} mal das Lautstaerkelimit von {limit} ueberschritten, deine Talk Power wurde entzogen!"
            tp = client.channel.neededTalkPower
            if not tp or tp < 1 or tp == "-1":
                ts3lib.requestSetClientChannelGroup(schid, [self.tabs[schid]["channelBanGroup"]], [client.channel.channelID], [client.databaseID])
            err = ts3lib.requestClientSetIsTalker(schid, clid, False)
            if err != ts3defines.ERROR_ok: return
            client.sendTextMsg(msg.replace("{violations}",str(self.maxviolations)).replace("{limit}",str(self.maxlevel)))
            return
        if level > self.maxlevel:
            self.clients[clid] += 1
            print(clid, level, self.clients[clid])

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        srv = self.ts3host.getServer(schid)
        if clid == srv.me.clientID:
            self.clients = {}
            (err, clids) = ts3lib.getChannelClientList(schid, newChannelID)
            for clid in clids:
                if clid == srv.me.clientID: continue
                self.onClientMoveEvent(schid, clid, 0, srv.me.channel.channelID, ts3defines.Visibility.ENTER_VISIBILITY, "")
            return
        if not srv.me.channel.channelID in [newChannelID, oldChannelID]: return
        # if not srv.me.getChannelGroupId() in [self.tabs[schid]["channelModGroup"],srv.defaultChannelAdminGroup]: return
        # (err, perm) = ts3lib.getClientNeededPermission(schid, "b_client_set_flag_talker")
        # if not perm: return
        if newChannelID == srv.me.channel.channelID:
            client = srv.getUser(clid)
            if client.getChannelGroupId() != srv.defaultChannelGroup: return
            status = getContactStatus(srv.me.uid)
            if status == ContactStatus.FRIEND: return
            self.clients[clid] = 0
        elif oldChannelID == srv.me.channel.channelID:
            if clid in self.clients: del self.clients[clid]

"""
    fullchannel: 0 newChannelID: 0
Error calling method onClientMoveEvent of plugin Channel Queue: Traceback (most recent call last):
  File "C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/scripts\pluginhost.py", line 394, in invokePlugins
    ret.append(meth(*args))
  File "C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/scripts\joinChannel\__init__.py", line 77, in onClientMoveEvent
    ts3lib.setChannelVariableAsInt(schid, newChannelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, maxclients - 1)
TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'
"""