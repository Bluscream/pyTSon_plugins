import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin
from datetime import datetime

class gommeHD(ts3plugin):
    name = "GommeHD nifty tricks"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = True
    suid = "QTRtPmYiSKpMS8Oyd4hyztcvLqU="
    channelAdminGroupID = 10
    gommeBotNick = "Gomme-Bot"
    msg = "um nur Personen ab dem ausgewählen Rang die Möglichkeit zu geben, in deinen Channel zu joinen."
    gommeBotID = 0

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if fromUniqueIdentifier != "serveradmin": return
        if fromName != self.gommeBotNick: return
        if self.gommeBotID == 0: self.gommeBotID = fromID
        # if not message.endswith(self.msg): return
        # ts3lib.requestSendPrivateTextMsg(schid, "registriert", fromID)

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        # if self.debug: ts3lib.printMessageToCurrentTab('suid != self.suid: {}'.format(suid != self.suid))
        if suid != self.suid: return
        (err, ownID) = ts3lib.getClientID(schid)
        # if self.debug: ts3lib.printMessageToCurrentTab('clientID != ownID: {}'.format(clientID != ownID))
        if clientID != ownID: return
        # if self.debug: ts3lib.printMessageToCurrentTab('channelGroupID != self.channelAdminGroupID: {}'.format(channelGroupID != self.channelAdminGroupID))
        if channelGroupID != self.channelAdminGroupID: return
        # if self.debug: ts3lib.printMessageToCurrentTab('invokerClientID != 0: {}'.format(invokerClientID != 0))
        if invokerClientID == 0:
            (err, ntp) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
            if not ntp or ntp == 0: ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER, 23)
            # (err, cmc) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
            ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_MAXCLIENTS_UNLIMITED, 0)
            ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, 10)
            (err, cnp) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC)
            if not cnp or cnp == "": ts3lib.setChannelVariableAsString(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC, "Team | Lounge 1")
            ts3lib.flushChannelUpdates(schid, channelID)
        # clid = ts3lib.getClientIDbyNickname(schid, self.gommeBotNick)
        # if not clid: ts3lib.printMessage(schid, 'Gomme-Bot not found.', ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
        # (err, uid) = ts3lib.getClientVariable(schid, self.gommeBotID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        # if uid != "serveradmin": return
        # if self.debug: ts3lib.printMessageToCurrentTab('self.gommeBotID == 0: {}'.format(self.gommeBotID == 0))
        if self.gommeBotID == 0: return
        ts3lib.requestSendPrivateTextMsg(schid, "registriert", self.gommeBotID)