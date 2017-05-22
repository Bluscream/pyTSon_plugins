import ts3lib, ts3defines, datetime
from ts3plugin import ts3plugin, PluginHost
from pytson import getPluginPath
from os import path

class faker(ts3plugin):
    name = "Fake Anything"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Fake almost anything ;)"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    iconPath = path.join(getPluginPath(), "scripts", "faker", "icons")
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Fake this channel", iconPath+"/fake.png"),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Fake this client", iconPath+"/fake.png")]
    hotkeys = []


    def __init__(self):
        ts3lib.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug:
            ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL and menuItemID == 0: self.fakeChannel(schid, selectedItemID)
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT and menuItemID == 0: self.fakeClient(schid, selectedItemID)

    def fakeChannel(self, schid, channelID):
        (error, nick) = ts3lib.getChannelVariableAsString(schid, channelID, ts3defines.ChannelProperties.CHANNEL_NAME)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_NAME,nick)

        (error, phonetic) = ts3lib.getChannelVariableAsString(schid, channelID, ts3defines.ChannelProperties.CHANNEL_NAME_PHONETIC)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_NAME,phonetic)

        (error, pw) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_PASSWORD)
        if pw: ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_PASSWORD,".")

        (error, topic) = ts3lib.getChannelVariableAsString(schid, channelID, ts3defines.ChannelProperties.CHANNEL_TOPIC)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_TOPIC,topic)

        (error, description) = ts3lib.getChannelVariableAsString(schid, channelID, ts3defines.ChannelProperties.CHANNEL_DESCRIPTION)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_DESCRIPTION,description)

        (error, neededtp) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_NEEDED_TALK_POWER)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_NEEDED_TALK_POWER,neededtp)

        (error, codec) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_CODEC,codec)

        (error, quality) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC_QUALITY)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_CODEC_QUALITY,quality)

        (error, latency) = ts3lib.getChannelVariableAsString(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC_LATENCY_FACTOR)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_CODEC_LATENCY_FACTOR,latency)

        (error, unencrypted) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC_IS_UNENCRYPTED)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_CODEC_IS_UNENCRYPTED,unencrypted)

        (error, maxclients) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS,maxclients)

        (error, maxfamilyclients) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXFAMILYCLIENTS)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_MAXFAMILYCLIENTS,maxfamilyclients)

        (error, iconid) = ts3lib.getChannelVariableAsUint64(schid, channelID, ts3defines.ChannelProperties.CHANNEL_ICON_ID)
        ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_ICON_ID,iconid)

        (error, _clid) = ts3lib.getClientID(schid)

    def fakeClient(self, schid, clientID):
        (error, _clid) = ts3lib.getClientID(schid)
        (error, tnick) = ts3lib.getClientVariableAsUInt64(schid, clientID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        (error, tnickp) = ts3lib.getClientVariableAsUInt64(schid, clientID, ts3defines.ClientProperties.CLIENT_NICKNAME_PHONETIC)
