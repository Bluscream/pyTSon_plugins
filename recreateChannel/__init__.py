import ts3defines, ts3lib, json
from ts3plugin import ts3plugin
from datetime import datetime

class recreateChannel(ts3plugin):
    name = "Recreate Channel"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Check out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Recreate Channel", "")]
    hotkeys = []
    debug = False

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        err, clientID = ts3lib.getClientID(schid)
        err, channelID = ts3lib.getChannelOfClient(schid, clientID)
        # CHANNEL_NAME
        err, self.CHANNEL_NAME = ts3lib.getChannelVariableAsString(schid, channelID, ts3defines.ChannelProperties.CHANNEL_NAME)
        ts3lib.setChannelVariableAsString(schid,0,ts3defines.ChannelProperties.CHANNEL_NAME,self.CHANNEL_NAME+"_")
        # CHANNEL_NAME_PHONETIC
        err, CHANNEL_NAME_PHONETIC = ts3lib.getChannelVariableAsString(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC)
        ts3lib.setChannelVariableAsString(schid,0,ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC,CHANNEL_NAME_PHONETIC)
        # CHANNEL_TOPIC
        # err, CHANNEL_TOPIC = ts3lib.getChannelVariableAsString(schid, channelID, ts3defines.ChannelProperties.CHANNEL_TOPIC)
        # ts3lib.setChannelVariableAsString(schid,0,ts3defines.ChannelProperties.CHANNEL_TOPIC,CHANNEL_TOPIC)
        # CHANNEL_DESCRIPTION
        # err, CHANNEL_DESCRIPTION = ts3lib.getChannelVariableAsString(schid, channelID, ts3defines.ChannelProperties.CHANNEL_DESCRIPTION)
        # ts3lib.setChannelVariableAsString(schid,0,ts3defines.ChannelProperties.CHANNEL_DESCRIPTION,CHANNEL_DESCRIPTION)
        # CHANNEL_CODEC
        err, CHANNEL_CODEC = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC)
        ts3lib.setChannelVariableAsInt(schid,0,ts3defines.ChannelProperties.CHANNEL_CODEC,CHANNEL_CODEC)
        # CHANNEL_CODEC_QUALITY
        err, CHANNEL_CODEC_QUALITY = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC_QUALITY)
        ts3lib.setChannelVariableAsInt(schid,0,ts3defines.ChannelProperties.CHANNEL_CODEC_QUALITY,CHANNEL_CODEC_QUALITY)
        # CHANNEL_MAXCLIENTS
        err, CHANNEL_MAXCLIENTS = ts3lib.getChannelVariableAsUInt64(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        ts3lib.setChannelVariableAsUInt64(schid,0,ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS,CHANNEL_MAXCLIENTS)
        # CHANNEL_MAXFAMILYCLIENTS
        err, CHANNEL_MAXFAMILYCLIENTS = ts3lib.getChannelVariableAsUInt64(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXFAMILYCLIENTS)
        ts3lib.setChannelVariableAsUInt64(schid,0,ts3defines.ChannelProperties.CHANNEL_MAXFAMILYCLIENTS,CHANNEL_MAXFAMILYCLIENTS)
        # CHANNEL_NEEDED_TALK_POWER
        err, CHANNEL_NEEDED_TALK_POWER = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        ts3lib.setChannelVariableAsInt(schid,0,ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER,CHANNEL_NEEDED_TALK_POWER)
        # self.returncode = ts3lib.createReturnCode()
        ts3lib.ﬂushChannelCreation(schid, 0)#, self.returncode)


    def onNewChannelCreatedEvent(self, schid, channelID, channelParentID, invokerID, invokerName, invokerUniqueIdentiﬁer):
        err, clientID = ts3lib.getClientID(schid)
        if invokerID != clientID: return
        ts3lib.setChannelVariableAsString(schid,channelID,ts3defines.ChannelProperties.CHANNEL_NAME,self.CHANNEL_NAME)
        del self.CHANNEL_NAME
        ts3lib.ﬂushChannelUpdates(schid, channelID)
