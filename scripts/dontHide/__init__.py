import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from PythonQt.QtCore import QTimer
from bluscream import timestamp, intList, getContactStatus, ContactStatus, sendCommand

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
    infoTitle = None
    menuItems = []
    hotkeys = []
    timer = QTimer()
    ts3host = None

    def __init__(self):
        if "aaa_ts3Ext" in PluginHost.active:
            ts3ext = PluginHost.active["aaa_ts3Ext"]
            self.ts3host = ts3ext.ts3host
            del self.timer
        else:
            retry = 1000
            self.timer.singleShot(retry, self.__init__)
            ts3lib.printMessageToCurrentTab("{}: [color=red]Dependency not yet loaded, retrying in {} second(s)!".format(self.name, retry/1000))
            return
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        if hasattr(self, "timer"):
            if self.timer.isActive(): self.timer.stop()
            del self.timer

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        if not newChannelID: return
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