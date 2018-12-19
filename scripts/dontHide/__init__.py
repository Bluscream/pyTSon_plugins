import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from PythonQt.QtCore import QTimer
from bluscream import timestamp, intList, getContactStatus, ContactStatus, sendCommand
# from ts3Ext import ts3SessionHost as ts3host

class dontHide(ts3plugin):
    name = "Don't Hide"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Shows clients that hide."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = " "
    menuItems = []
    hotkeys = []
    timer = QTimer()
    ts3host = None

    def __init__(self):
        if "aaa_ts3Ext" in PluginHost.active:
            ts3ext = PluginHost.active["aaa_ts3Ext"]
            self.ts3host = ts3ext.ts3host
            ts3lib.logMessage("{}: Dependency loaded".format(self.name), ts3defines.LogLevel.LogLevel_WARNING, "pyTSon", 0)
        else:
            retry = 1000
            self.timer.singleShot(retry, self.__init__)
            ts3lib.logMessage("{}: Dependency not yet loaded, retrying in {} second(s)!".format(self.name, retry/1000), ts3defines.LogLevel.LogLevel_WARNING, "pyTSon", 0)
            return
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        if hasattr(self, "timer"):
            if self.timer.isActive(): self.timer.stop()

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        counts = self.getClientCounts(schid)
        if counts["hidden"]["total"] > 0:
            ts3lib.printMessage(schid, "[color=orange][b]{}[/b] hidden users on this server!".format(counts["hidden"]["total"]), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)

    def getClientCounts(self, schid):
        ret = {"total": {}, "visible": {}, "hidden": {}}
        visible = self.ts3host.getServer(schid).users
        ret["visible"]["users"] = 0
        ret["visible"]["queries"] = 0
        for user in visible:
            (err, ctype) = ts3lib.getClientVariable(schid, user.clientID, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
            if ctype == ts3defines.ClientType.ClientType_NORMAL: ret["visible"]["users"] += 1
            elif ctype == ts3defines.ClientType.ClientType_SERVERQUERY: ret["visible"]["queries"] += 1
        ret["visible"]["total"] = ret["visible"]["users"]+ret["visible"]["queries"] # len(visible)
        (err, ret["total"]["clients"]) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_CLIENTS_ONLINE)
        (err, ret["total"]["queries"]) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_QUERYCLIENTS_ONLINE)
        (err, ret["max"]) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_MAXCLIENTS)
        ret["hidden"]["total"] = ret["total"]["clients"]-ret["visible"]["total"]
        return ret

    def infoData(self, schid, aid, atype):
        if atype != ts3defines.PluginItemType.PLUGIN_SERVER: return
        counts = self.getClientCounts(schid)
        # if counts["hidden"]["total"] > 0:
        return ["Shown Clients: %s"%counts["visible"]["users"], "Shown Queries: %s"%counts["visible"]["queries"], "Hidden: %s"%counts["hidden"]["total"], "{}".format(counts)]
        # return None # ["clients:%s"%clients, "queries:%s"%queries, "max:%s"%max, "visible_users:%s"%visible_users, "visible_queries:%s"%visible_queries]

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        if not newChannelID: return
        return
        if visibility == ts3defines.Visibility.LEAVE_VISIBILITY:
            cmd = "notifycliententerview"
            client = self.buildClient(schid, clid, oldChannelID, newChannelID)
            for k in client:
                if client[k] != "":
                    cmd += " {}={}".format(k, client[k])
                else: cmd += " {}".format(k)
            sendCommand(self.name, cmd, schid, False, True)

    def buildClient(self, schid, clid, oldChannelID, newChannelID):
        _client = self.ts3host.getUser(schid, clid)
        client = dict()
        client["reasonid"] = "0"
        client["cfid"] = oldChannelID
        client["ctid"] = newChannelID
        client["client_channel_group_id"] = _client.getChannelGroupId()
        (err, client["client_servergroups"]) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        (err, client["client_channel_group_inherited_channel_id"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_INHERITED_CHANNEL_ID)
        client["client_input_muted"] = _client.isInputMuted
        client["client_output_muted"] = _client.isOutputMuted
        client["client_outputonly_muted"] = _client.isOutputOnlyMuted
        (err, client["client_input_hardware"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_INPUT_HARDWARE)
        (err, client["client_output_hardware"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_OUTPUT_HARDWARE)
        client["client_is_recording"] = _client.isRecording
        (err, client["client_type"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
        client["client_is_talker"] = _client.isTalker
        client["client_away"] = _client.isAway
        client["client_is_channel_commander"] = _client.isChannelCommander
        (err, client["client_is_priority_speaker"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_IS_PRIORITY_SPEAKER)
        client["clid"] = clid
        client["client_database_id"] = _client.databaseID
        client["client_talk_power"] = _client.talkPower
        (err, client["client_unread_messages"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_UNREAD_MESSAGES)
        (err, client["client_needed_serverquery_view_power"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_NEEDED_SERVERQUERY_VIEW_POWER)
        client["client_icon_id"] = _client.iconID
        client["client_unique_identifier"] = _client.uniqueIdentifier
        client["client_nickname"] = _client.name
        (err, client["client_meta_data"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_META_DATA)
        (err, client["client_away_message"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_AWAY_MESSAGE)
        (err, client["client_flag_avatar"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_FLAG_AVATAR)
        (err, client["client_talk_request"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_OUTPUT_HARDWARE)
        (err, client["client_talk_request_msg"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_TALK_REQUEST_MSG)
        client["client_description"] = _client.description
        (err, client["client_nickname_phonetic"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_NICKNAME_PHONETIC)
        (err, client["client_country"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_COUNTRY)
        (err, client["client_badges"]) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_BADGES)
        return client


"""
[IN ] notifyclientleftview cfid=32 ctid=2811786 reasonid=0 clid=120
Error calling method onClientMoveEvent of plugin Don't Hide: Traceback (most recent call last):
  File "C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/scripts\pluginhost.py", line 394, in invokePlugins
    ret.append(meth(*args))
  File "C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/scripts\dontHide\__init__.py", line 41, in onClientMoveEvent
    client = self.buildClient(schid, clid, oldChannelID, newChannelID)
  File "C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/scripts\dontHide\__init__.py", line 54, in buildClient
    client["client_channel_group_id"] = _client.getChannelGroupId()
  File "C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/include\ts3Ext\__init__.py", line 910, in getChannelGroupId
    if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client channel group id: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
ts3Ext.ts3Error: Error getting client channel group id: (512, invalid clientID)
"""