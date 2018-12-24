import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp, getScriptPath, getChannelPassword, getContactStatus, channelURL
from ts3enums import ContactStatus

class TS3AB(ts3plugin):
    path = getScriptPath(__name__)
    name = "TS3AB"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID: return
        (err, needed_tp) = ts3lib.getChannelVariable(schid, newChannelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        if needed_tp >=0:
            # (err, hasTP) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
            (err, ownTP) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_TALK_POWER)
            if int(ownTP) < needed_tp: ts3lib.requestSendPrivateTextMsg(schid, self.text, self.servers[schid]["clid"], self.retcode) # ts3lib.requestIsTalker(schid, True, "")