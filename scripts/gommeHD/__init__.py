import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from datetime import datetime
from PythonQt.QtCore import QTimer
from collections import defaultdict
from bluscream import timestamp, getContactStatus, ContactStatus

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
    hotkeys = []
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Ask for avatar", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Send Steam", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Send Steam", "")
    ]
    suid = "QTRtPmYiSKpMS8Oyd4hyztcvLqU="
    channelAdminGroupID = 10
    gommeBotNick = "Gomme-Bot"
    delay = 1500
    settings = { "maxclients": 10, "tp": 23 }
    violations = defaultdict(int)
    askForAvatar = False
    alreadyAsked = []
    msg = "um nur Personen ab dem ausgewählen Rang die Möglichkeit zu geben, in deinen Channel zu joinen."
    blockMSG = "Diesen Befehl kannst du nur als Channel-Admin ausführen!"
    welcomeMSG = ['Gomme-Bot geöffnet! Tippe "ruhe", um den Ruhe-Rang zu erhalten!','Du möchtest nicht mehr angeschrieben werden? Tippe "togglebot"']
    steammsg = """
Steam: [url]https://steamcommunity.com/profiles/76561198022446661[/url]
Add as friend: [url]steam://friends/add/76561198022446661[/url]
Common games: [url]https://steamcommunity.com/profiles/76561198022446661/games/?tab=all&games_in_common=1[/url]
Account Value: [url]https://steamdb.info/calculator/76561198022446661/?cc=eu[/url]
Trade URL: [url]https://steamcommunity.com/tradeoffer/new/?partner=62180933&token=fSMYHMGM[/url]
"""
    avatarmsg = """Hey {nick}, es wäre voll knorke von dir wenn du mir erlauben würdest dein Premium zu benutzen damit ich mir nen avatar setzen kann.
Dabei gehst du keine scam Gefahr ein weil du mir das jederzeit wieder wegnehmen kannst auch wenn ich schon disconnected bin (frag jeden das ist so)
Ich erklär dir auch wie's geht:
1. Geh auf den Gomme minecraft server und gib [color=red]/ts set {myuid}[/color] ein und schreib mir in TS deinen minecraft namen.
2. Ich werde deinen mc namen dem gomme bot schreiben damit er mir premium geben kann
3. Wenn ich dann Premium habe werde ich mir kurz nen avatar setzen max. 2 min
4. Dann sag ich dir bescheid und du gibst in minecraft [color=green]/ts set {uid}[/color] ein und hast dein premium wieder
5. Ich werde mich bei dir bedanken ;) 
"""

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID != 0: return
        if atype == ts3defines.PluginItemType.PLUGIN_SERVER:
            self.askForAvatar = not self.askForAvatar
        if atype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
            ts3lib.requestSendChannelTextMsg(schid, self.steammsg, selectedItemID)
        elif atype == ts3defines.PluginItemType.PLUGIN_CLIENT:
            ts3lib.requestSendPrivateTextMsg(schid, self.steammsg, selectedItemID)

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if fromUniqueIdentifier != "serveradmin": return False
        if fromName != self.gommeBotNick: return False
        if message.endswith(self.msg):
            self.schid = schid; self.gommeBotID = fromID
            QTimer.singleShot(self.delay, self.sendMessage)
        elif message in self.welcomeMSG: return True
        elif message == self.blockMSG: QTimer.singleShot(self.delay, self.sendMessage)

    def sendMessage(self):
        ts3lib.requestSendPrivateTextMsg(self.schid, "registriert", self.gommeBotID)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.askForAvatar: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        if oldChannelID != 0: return
        (err, uid) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if getContactStatus(uid) == ContactStatus.BLOCKED: return
        if uid in self.alreadyAsked: return
        (err, sgroups) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        if 17 in sgroups: return
        if set(sgroups).isdisjoint([31,30,14]): return
        (err, myuid) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        (err, nick) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        ts3lib.requestSendPrivateTextMsg(schid, self.avatarmsg.replace("{nick}", nick).replace("{myuid}", myuid).replace("{uid}", uid), clientID)
        self.alreadyAsked.append(uid)

    def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID: return
        if channelGroupID != self.channelAdminGroupID: return
        if invokerClientID == 0:
            (err, ntp) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
            if not ntp or ntp == 0: ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER, self.settings["tp"])
            ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_MAXCLIENTS_UNLIMITED, 0)
            ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, self.settings["maxclients"])
            (err, cnp) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC)
            if not cnp or cnp == "": ts3lib.setChannelVariableAsString(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC, "Team | Lounge 1")
            ts3lib.flushChannelUpdates(schid, channelID)
        return
        if self.gommeBotID == 0: return
        ts3lib.requestSendPrivateTextMsg(schid, "registriert", self.gommeBotID)

    def onUpdateChannelEditedEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentifier):
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        (err, ownID) = ts3lib.getClientID(schid)
        if invokerID == ownID:
            (err, self.settings["maxclients"]) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
            (err, self.settings["tp"]) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        (err, ownChannel) = ts3lib.getChannelOfClient(schid, ownID)
        if channelID != ownChannel: return
        (err, invokerChannel) = ts3lib.getChannelOfClient(schid, invokerID)
        if invokerChannel == channelID: return
        _needed = False
        (err, ntp) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        if ntp != self.settings["tp"]:
            _needed = True
            ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER, self.settings["tp"])
        (err, cmc) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_MAXCLIENTS_UNLIMITED, 0)
        if cmc != self.settings["maxclients"]:
            _needed = True
            ts3lib.setChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS, self.settings["maxclients"])
        if _needed:
            ts3lib.flushChannelUpdates(schid, channelID)
            self.violations[invokerUniqueIdentifier] += 1
            if self.violations[invokerUniqueIdentifier] > 2:
                (err, dbid) = ts3lib.getClientVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                ts3lib.requestSetClientChannelGroup(schid, [9], [channelID], [dbid])
                del self.violations[invokerUniqueIdentifier]