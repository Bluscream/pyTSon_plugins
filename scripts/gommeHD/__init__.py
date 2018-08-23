# coding=utf-8
import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from datetime import datetime
from PythonQt.QtCore import QTimer
from collections import defaultdict
from random import choice
from bluscream import timestamp, getContactStatus, ContactStatus, parseCommand, clientURL, inputBox

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
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Ask for avatar", "scripts/%s/ask_for_avatar.png"%__name__),
                (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Dynamic Silence", ""),
                (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Send Steam", "scripts/%s/steam.png"%__name__),
                (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Send Steam", "scripts/%s/steam.png"%__name__),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 1, "Toggle aka", "")]
    suid = "QTRtPmYiSKpMS8Oyd4hyztcvLqU="
    channelAdminGroupID = 10
    premiumGroupIDs = ["31","30","14"]
    ruheGroupID = "17"
    gommeBotNick = "Gomme-Bot"
    dynamicSilenceName = "msg me"
    delay = 1500
    nick_enabled = False
    nicknames = ["Qmx1c2NyZWFt=","Q2hyaXN0b3BoZXIgQXVyaWNo=","RGFubnkgUmFkbWFjaGVy="]
    settings = { "maxclients": 10, "tp": 23 }
    violations = defaultdict(int)
    askForAvatar = False
    dynamicSilence = True
    alreadyAsked = []
    schid = 0
    clids = []
    dynamicSilenceCache = []
    gommeBotID = 0
    timer = QTimer()
    aka = (0, 0, "", "")
    msg = "um nur Personen ab dem ausgewählen Rang die Möglichkeit zu geben, in deinen Channel zu joinen."
    blockMSG = "Diesen Befehl kannst du nur als Channel-Admin ausführen!"
    ignoreMSG = ['Gomme-Bot geöffnet! Tippe "ruhe", um den Ruhe-Rang zu erhalten!','Du möchtest nicht mehr angeschrieben werden? Tippe "togglebot"', "Bevor du alle Funktionalitäten nutzen kannst, musst du unseren Nutzungsbedingungen und der Datenschutzerklärung zustimmen. Diese findest du auf https://gommehd.net/terms/teamspeak/de/"]
    agreeMSG = "Schreibe \"agree\" in den Chat, um deine Zustimmung zu erteilen."
    steammsg = """
Steam: [url]https://steamcommunity.com/profiles/76561198022446661[/url]
Add as friend: [url]steam://friends/add/76561198022446661[/url]
Common games: [url]https://steamcommunity.com/profiles/76561198022446661/games/?tab=all&games_in_common=1[/url]
Account Value: [url]https://steamdb.info/calculator/76561198022446661/?cc=eu[/url]
Trade URL: [url]https://steamcommunity.com/tradeoffer/new/?partner=62180933&token=fSMYHMGM[/url]
Live Broadcast: [url]https://steamcommunity.com/broadcast/watch/76561198022446661[/url]
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
        self.timer.timeout.connect(self.tick)
        self.timer.setTimerType(2)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def menuCreated(self): self.checkMenus()

    def currentServerConnectionChanged(self, schid): self.checkMenus(schid)

    def checkMenus(self, schid=0):
        if not self.name in PluginHost.active: return
        if schid < 1: schid = ts3lib.getCurrentServerConnectionHandlerID()
        err, status = ts3lib.getConnectionStatus(schid)
        if status != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: self.toggleMenus(False)
        else: self.toggleMenus(True)

    def toggleMenus(self, enabled):
        for menuItem in self.menuItems:
            try: ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, menuItem[1]), enabled)
            except: pass

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginItemType.PLUGIN_SERVER:
            if menuItemID == 0:
                self.dynamicSilence = not self.dynamicSilence
                ts3lib.printMessageToCurrentTab("{}{}: DynamicSilence set to [color=orange]{}".format(timestamp(),self.name,self.dynamicSilence))
            elif menuItemID == 1:
                self.askForAvatar = not self.askForAvatar
                ts3lib.printMessageToCurrentTab("{}askForAvatar set to [color=orange]{}".format(timestamp(),self.askForAvatar))
                if not self.askForAvatar:
                    self.clids = []
                    self.timer.stop()
                    return
                (err, clids) = ts3lib.getClientList(schid)
                for c in clids: ts3lib.requestClientVariables(schid, c)
                for c in clids:
                    (err, uid) = ts3lib.getClientVariable(schid, c, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                    if getContactStatus(uid) == ContactStatus.BLOCKED: continue
                    if uid in self.alreadyAsked: continue
                    (err, sgroups) = ts3lib.getClientVariableAsString(schid, c, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
                    sgroups = sgroups.split(",")
                    if self.ruheGroupID in sgroups: continue
                    if set(sgroups).isdisjoint(self.premiumGroupIDs): continue
                    self.clids.append(c)
                ts3lib.printMessageToCurrentTab("{}Asking {} clients for avatar".format(timestamp(),len(self.clids)))
                self.schid = schid
                self.timer.start(1000)
        if atype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
            ts3lib.requestSendChannelTextMsg(schid, self.steammsg, selectedItemID)
        elif atype == ts3defines.PluginItemType.PLUGIN_CLIENT:
            if menuItemID == 0:
                ts3lib.requestSendPrivateTextMsg(schid, self.steammsg, selectedItemID)
            elif menuItemID == 1:
                print(self.aka)
                if self.aka != (0, 0, "", ""):
                    self.aka = (0, 0, "", "")
                    return
                realname = inputBox(self.name, "Real name:")
                if not realname: return
                (err, name) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_NICKNAME)
                ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, "{} aka {}".format(realname, name))
                ts3lib.flushClientSelfUpdates(schid)
                self.aka = (schid, selectedItemID, realname, name)

    def tick(self):
        if not self.askForAvatar or not self.schid or len(self.clids) < 1: self.timer.stop(); return
        (err, myuid) = ts3lib.getClientSelfVariable(self.schid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        (err, uid) = ts3lib.getClientVariable(self.schid, self.clids[0], ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        (err, nick) = ts3lib.getClientVariable(self.schid, self.clids[0], ts3defines.ClientProperties.CLIENT_NICKNAME)
        ts3lib.requestSendPrivateTextMsg(self.schid, self.avatarmsg.replace("{nick}", nick).replace("{myuid}", myuid).replace("{uid}", uid), self.clids[0])
        self.alreadyAsked.append(uid)
        del self.clids[0]

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if fromUniqueIdentifier != "serveradmin": return
        if fromName != self.gommeBotNick: return
        if message.endswith(self.msg):
            self.schid = schid; self.gommeBotID = fromID
            QTimer.singleShot(self.delay, self.sendMessage)
        elif message == self.blockMSG: QTimer.singleShot(self.delay, self.sendMessage)
        elif message == self.agreeMSG: ts3lib.requestSendPrivateTextMsg(self.schid, "agree", self.gommeBotID); return True
        elif message in self.ignoreMSG: return True

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
        (err, sgroups) = ts3lib.getClientVariableAsString(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        sgroups = sgroups.split(",")
        if self.ruheGroupID in sgroups: return
        if set(sgroups).isdisjoint(self.premiumGroupIDs): return
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
        if self.gommeBotID < 1: return
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

    def onUpdateClientEvent(self, schid, clid, invokerID, invokerName, invokerUniqueIdentifier):
        if schid != self.aka[0]: return
        if clid != self.aka[1]: return
        (err, name) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if name == self.aka[3]: return
        ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, "{} aka {}".format(self.aka[2], name))
        ts3lib.flushClientSelfUpdates(schid)

    def onIncomingClientQueryEvent(self, schid, commandText):
        if not self.dynamicSilence: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        if commandText.split(" ", 1)[0] != "notifyclientupdated": return
        cmd, params = parseCommand(commandText)
        if len(params) > 0 and "client_nickname" in params:
            clid = int(params["clid"])
            # (err, ownID) = ts3lib.getClientID(schid)
            # if clid == ownID: return
            (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            if getContactStatus(uid) != ContactStatus.FRIEND: return
            if not self.dynamicSilenceName in params["client_nickname"].lower(): return
            ts3lib.requestSendPrivateTextMsg(schid, "Yes, {}-{}?".format(clientURL(schid, clid), choice(["chan","san"])), clid)
            # ts3lib.printMessageToCurrentTab("{} {}".format(cmd, params)) # ["client_nickname"][1]

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        if not self.nick_enabled: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, choice(self.nicknames))
        ts3lib.flushClientSelfUpdates(schid)