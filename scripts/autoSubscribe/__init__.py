import ts3lib, ts3defines, datetime
from ts3plugin import ts3plugin, PluginHost
from pytson import getPluginPath, getCurrentApiVersion
from os import path
from bluscream import timestamp
from PythonQt.QtCore import QTimer

blacklist = [".fm", "radio", "music", "musik"]
passwords = ["pw", "pass"]

def isSubscribed(schid, cid):
    (error, subscribed) = ts3lib.getChannelVariableAsInt(schid, cid, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_ARE_SUBSCRIBED)
    if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Channel #{} is {}".format(cid, "[color=red]subscribed" if subscribed else "[color=green]not subscribed"))
    return bool(subscribed)

def isPassworded(schid, cid):
    (error, pw) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
    if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Channel #{} is {}".format(cid, "[color=red]passworded" if pw else "[color=green]not passworded"))
    return bool(pw)

def isBlacklisted(schid, cid):
    (error, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
    if PluginHost.cfg.getboolean("general", "verbose"):
        bl = []
        for b in blacklist:
            if b in name.lower(): bl.append(b)
        ts3lib.printMessageToCurrentTab("Channel #{} is {} ({})".format(cid, "[color=red]blacklisted ({})".format(", ".join(bl)) if any(x in name.lower() for x in blacklist) else "[color=green]not blacklisted", name))
    return any(x in name.lower() for x in blacklist)

def isPWInName(schid, cid):
    (error, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
    if PluginHost.cfg.getboolean("general", "verbose"):
        bl = []
        for b in passwords:
            if b in name.lower(): bl.append(b)
        ts3lib.printMessageToCurrentTab("Channel #{} {} [{}]".format(cid, "[color=yellow]has pw in name ({})".format(", ".join(bl)) if any(x in name.lower() for x in passwords) else "[color=grey]doesn't have pw in name", name))
    return any(x in name.lower() for x in passwords)

def isMusicChannel(schid, cid):
    (error, codec) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_CODEC)
    if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Channel #{} is {} ({})".format(cid, "[color=red]music channel".format() if codec == 5 else "[color=green]no music channel", codec))
    return codec == ts3defines.CodecType.CODEC_OPUS_MUSIC

def isPermanent(schid, cid):
    (error, permanent) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PERMANENT)
    if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Channel #{} is {}".format(cid, "[color=red]permanent" if permanent else "[color=green]not permanent"))
    return bool(permanent)

def isSemiPermanent(schid, cid):
    (error, semipermanent) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_SEMI_PERMANENT)
    if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Channel #{} is {}".format(cid, "[color=red]semi permanent" if semipermanent else "[color=green]not semi permanent"))
    return bool(semipermanent)


class autoSubscribe(ts3plugin):
    name = "Auto Subscribe"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Manage your channel subscriptions the way YOU want."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    iconPath = path.join(getPluginPath(), "scripts", "autoSubscribe", "icons")
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Subscribe to all channels", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Sub all non-pw channels", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "Sub all visible-pw channels", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 3, "Unsub from all channels", "")]
    hotkeys = []
    subAll = []
    subOpen = []
    subNone = []
    isFlooding = False
    schid = 0
    toSub = []
    # subscribeOpen TODO

    def __init__(self):
        self.schid = ts3lib.getCurrentServerConnectionHandlerID()
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0: self.subscribeAll(schid)
            elif menuItemID == 1: self.subscribeOpen(schid)
            elif menuItemID == 2: self.subscribeOpenPW(schid)
            elif menuItemID == 3: self.unsubscribeAll(schid)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            (error, uid) = ts3lib.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
            self.schid = schid
            if uid in self.subAll: QTimer.singleShot(2500, self.subscribeAll)
            elif uid in self.subNone: QTimer.singleShot(2500, self.unsubscribeAll)
            elif uid in self.subOpen: QTimer.singleShot(2500, self.subscribeOpen)
            if uid == "QTRtPmYiSKpMS8Oyd4hyztcvLqU=":
                self.toSub = [136205,136209,545989]#support1-3,48=afk,46=iloveradio
                QTimer.singleShot(2500, self.subChannels)

    def subChannels(self, schid=0):
        if not schid: schid = self.schid
        if len(self.toSub) < 1: return
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Trying to subscribe {}".format(self.toSub))
        try:
            error = ts3lib.requestChannelSubscribe(schid, self.toSub)
            if not error == ts3defines.ERROR_ok: raise Exception("Error in requestChannelSubscribe")
        except:
            for cid in self.toSub: ts3lib.requestChannelSubscribe(schid, [cid])
        self.toSub = []

    def subscribeAll(self, schid=0):
        if not schid: schid = self.schid
        try:
            error = ts3lib.requestChannelSubscribeAll(schid)
            if not error == ts3defines.ERROR_ok: raise Exception("Error in requestChannelSubscribeAll")
        except:
            (error, clist) = ts3lib.getChannelList(schid)
            ts3lib.requestChannelSubscribe(schid, clist)

    def unsubscribeAll(self, schid=0):
        if not schid: schid = self.schid
        try:
            error = ts3lib.requestChannelUnsubscribeAll(schid)
            if not error == ts3defines.ERROR_ok: raise Exception("Error in requestChannelUnsubscribeAll")
        except:
            (error, clist) = ts3lib.getChannelList(schid)
            ts3lib.requestChannelUnsubscribe(schid, clist)

    def subscribeOpen(self, schid=0):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("==== subscribeOpen START ====")
        if not schid: schid = self.schid
        (error, clist) = ts3lib.getChannelList(schid)
        for c in clist:
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("==== #{0} ====".format(c))
            if not isSubscribed(schid, c) and not isPassworded(schid, c) and not isPermanent(schid, c) and not isSemiPermanent(schid, c) and not isMusicChannel(schid, c) and not isBlacklisted(schid, c):
                self.toSub.append(c)
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("==== #{0} ====".format(c))
        self.subChannels(schid)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("==== subscribeOpen END ====")

    def subscribeOpenPW(self, schid=0):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("==== subscribeOpenPW START ====")
        if not schid: schid = self.schid
        (error, clist) = ts3lib.getChannelList(schid)
        for c in clist:
            if not isSubscribed(schid, c) and not isPermanent(schid, c) and not isSemiPermanent(schid, c) and not isMusicChannel(schid, c) and not isBlacklisted(schid, c) and isPWInName(schid, c):
                self.toSub.append(c)
        self.subChannels(schid)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("==== subscribeOpenPW END ====")

    def onNewChannelCreatedEvent(self, schid, channelID, channelParentID, invokerID, invokerName, invokerUniqueIdentiﬁer):
        if not self.subscribeOpen: return False
        err, clid = ts3lib.getClientID(schid)
        if clid == invokerID: return False
        self.subscribe(schid, channelID)

    def onUpdateChannelEditedEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentiﬁer):
        if not self.subscribeOpen: return False
        err, clid = ts3lib.getClientID(schid)
        if clid == invokerID: return False
        self.subscribe(schid, channelID)

    def subscribe(self, schid, cid):
        subscribed = isSubscribed(schid, cid)
        if PluginHost.cfg.getboolean("general", "verbose"):
            ts3lib.printMessageToCurrentTab("==== #{0} ====".format(cid))
            ts3lib.printMessageToCurrentTab("Subscribed: {0}".format(subscribed))
            ts3lib.printMessageToCurrentTab("Passworded: {0}".format(isPassworded(schid, cid)))
            ts3lib.printMessageToCurrentTab("PWInName: {0}".format(isPWInName(schid, cid)))
            ts3lib.printMessageToCurrentTab("Blacklisted: {0}".format(isBlacklisted(schid, cid)))
            ts3lib.printMessageToCurrentTab("MusicChannel: {0}".format(isMusicChannel(schid, cid)))
            ts3lib.printMessageToCurrentTab("==== #{0} ====".format(cid))
        if not subscribed:
            if (isPassworded(schid, cid) and isPWInName(schid, cid)) or (not isPassworded(schid, cid) and not isBlacklisted(schid, cid) and not isMusicChannel(schid, cid)):
                return ts3lib.requestChannelSubscribe(schid, [cid])
        elif subscribed:
            if (isPassworded(schid, cid) and not isPWInName(schid, cid)) or isBlacklisted(schid, cid) or isMusicChannel(schid, cid):
                return ts3lib.requestChannelUnsubscribe(schid, [cid])
