from ts3plugin import ts3plugin, PluginHost
from bluscream import timestamp
import ts3defines, ts3lib

class silentError(ts3plugin):
    name = "Silent Errors"
    apiVersion = 21
    requestAutoload = False
    version = "1"
    author = "Bluscream"
    description = "Silences TeaSpeak's \"not implemented\" errors"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    notifycliententerview = {
        "cfid": "0",
        "ctid": "32",
        "reasonid": "0",
        "clid": "851",
        "client_unique_identifier": "9tbproHnVVtiWa3InJaDVwr\/NwE=",
        "client_nickname": "GuestPlayerXD999",
        "client_input_muted": "0",
        "client_output_muted": "0",
        "client_outputonly_muted": "0",
        "client_input_hardware": "0",
        "client_output_hardware": "1",
        "client_meta_data": "",
        "client_is_recording": "0",
        "client_database_id": "877756",
        "client_channel_group_id": "9",
        "client_servergroups": "10",
        "client_away": "0",
        "client_away_message": "",
        "client_type": "0",
        "client_flag_avatar": "",
        "client_talk_power": "3",
        "client_talk_request": "0",
        "client_talk_request_msg": "",
        "client_description": "",
        "client_is_talker": "0",
        "client_is_priority_speaker": "0",
        "client_unread_messages": "0",
        "client_nickname_phonetic": "",
        "client_needed_serverquery_view_power": "0",
        "client_icon_id": "0",
        "client_is_channel_commander": "0",
        "client_country": "DE",
        "client_channel_group_inherited_channel_id": "32",
        "client_badges": "Overwolf=0"
    }

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        return True

