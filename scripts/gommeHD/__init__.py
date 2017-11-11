import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtCore import QTimer
from collections import defaultdict

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
    debug = False
    suid = "QTRtPmYiSKpMS8Oyd4hyztcvLqU="
    channelAdminGroupID = 10
    gommeBotNick = "Gomme-Bot"
    msg = "um nur Personen ab dem ausgewählen Rang die Möglichkeit zu geben, in deinen Channel zu joinen."
    welcomeMSG = ['Gomme-Bot geöffnet! Tippe "ruhe", um den Ruhe-Rang zu erhalten!','Du möchtest nicht mehr angeschrieben werden? Tippe "togglebot"']
    delay = 750
    settings = { "maxclients": 10, "tp": 23 }
    violations = defaultdict(int)

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if fromUniqueIdentifier != "serveradmin": return False
        if fromName != self.gommeBotNick: return False
        if message.endswith(self.msg):
            self.schid = schid; self.gommeBotID = fromID
            QTimer.singleShot(self.delay, self.sendMessage)
        elif message in self.welcomeMSG: return True

    def sendMessage(self):
        ts3lib.requestSendPrivateTextMsg(self.schid, "registriert", self.gommeBotID)

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
            if not ntp or ntp == 0: ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER, self.settings["tp"])
            # (err, cmc) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
            ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_MAXCLIENTS_UNLIMITED, 0)
            ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, self.settings["maxclients"])
            (err, cnp) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC)
            if not cnp or cnp == "": ts3lib.setChannelVariableAsString(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC, "Team | Lounge 1")
            ts3lib.flushChannelUpdates(schid, channelID)
        return
        # clid = ts3lib.getClientIDbyNickname(schid, self.gommeBotNick)
        # if not clid: ts3lib.printMessage(schid, 'Gomme-Bot not found.', ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
        # (err, uid) = ts3lib.getClientVariable(schid, self.gommeBotID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        # if uid != "serveradmin": return
        # if self.debug: ts3lib.printMessageToCurrentTab('self.gommeBotID == 0: {}'.format(self.gommeBotID == 0))
        if self.gommeBotID == 0: return
        ts3lib.requestSendPrivateTextMsg(schid, "registriert", self.gommeBotID)

    def onUpdateChannelEditedEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentifier):
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        (err, ownID) = ts3lib.getClientID(schid)
        if self.debug: ts3lib.printMessageToCurrentTab('invokerID == ownID: {}'.format(invokerID == ownID))
        if invokerID == ownID:
            (err, self.settings["maxclients"]) = ts3lib.getChannelVariable(schid, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
            (err, self.settings["tp"]) = ts3lib.getChannelVariable(schid, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        (err, ownChannel) = ts3lib.getChannelOfClient(schid, ownID)
        if self.debug: ts3lib.printMessageToCurrentTab('channelID != ownChannel: {}'.format(channelID != ownChannel))
        if channelID != ownChannel: return
        (err, invokerChannel) = ts3lib.getChannelOfClient(schid, invokerID)
        if self.debug: ts3lib.printMessageToCurrentTab('invokerChannel == channelID: {}'.format(invokerChannel == channelID))
        if invokerChannel == channelID: return
        _needed = False
        (err, ntp) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        if self.debug: ts3lib.printMessageToCurrentTab('ntp != self.settings["tp"]: {}'.format(ntp != self.settings["tp"]))
        if ntp != self.settings["tp"]:
            _needed = True
            ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER, self.settings["tp"])
        (err, cmc) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_MAXCLIENTS_UNLIMITED, 0)
        if self.debug: ts3lib.printMessageToCurrentTab('cmc != self.settings["maxclients"]: {}'.format(cmc != self.settings["maxclients"]))
        if cmc != self.settings["maxclients"]:
            _needed = True
            ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, self.settings["maxclients"])
        if _needed:
            ts3lib.flushChannelUpdates(schid, channelID)
            self.violations[invokerUniqueIdentifier] += 1
            if self.debug: ts3lib.printMessageToCurrentTab("violations of {}: {}".format(invokerUniqueIdentifier, self.violations[invokerUniqueIdentifier]))
            if self.violations[invokerUniqueIdentifier] > 2:
                (err, dbid) = ts3lib.getClientVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                ts3lib.requestSetClientChannelGroup(schid, [9], [channelID], [dbid])
                del self.violations[invokerUniqueIdentifier]