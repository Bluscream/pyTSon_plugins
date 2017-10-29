import ts3lib, ts3defines, datetime
from ts3plugin import ts3plugin
from pytson import getPluginPath
from os import path
from PythonQt.QtCore import QTimer

blacklist = [".fm", "radio", "music", "musik"]
passwords = ["pw", "pass"]

def isPassworded(schid, cid):
    (error, pw) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
    return pw

def isBlacklisted(schid, cid):
    (error, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
    return any(x in name.lower() for x in blacklist)

def isPWInName(schid, cid):
    (error, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
    return any(x in name.lower() for x in passwords)

def isMusicChannel(schid, cid):
    (error, codec) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_CODEC)
    return codec == ts3defines.CodecType.CODEC_OPUS_MUSIC

def isPermanent(schid, cid):
    (error, permanent) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PERMANENT)
    return permanent

def isSemiPermanent(schid, cid):
    (error, semipermanent) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_SEMI_PERMANENT)
    return semipermanent


class autoSubscribe(ts3plugin):
    name = "Auto Subscribe"

    apiVersion = 22
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
    debug = False

    onlyOpen = False
    subAll = []
    subOpen = []
    subNone = []
    isFlooding = False
    schid = 0
    toSub = []

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

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
                self.toSub = [46,48,136205,136209,545989]
                QTimer.singleShot(2500, self.subChannels)

    def subChannels(self):
        for cid in self.toSub:
            ts3lib.requestChannelSubscribe(self.schid, [cid])
        del self.toSub

    def subscribeAll(self, schid=None):
        if not schid: schid = self.schid
        try:
            error = ts3lib.requestChannelSubscribeAll(schid)
            if not error == ts3defines.ERROR_ok: raise Exception("Error in requestChannelSubscribeAll")
        except:
            (error, clist) = ts3lib.getChannelList(schid)
            ts3lib.requestChannelSubscribe(schid, clist)

    def unsubscribeAll(self, schid=None):
        if not schid: schid = self.schid
        try:
            error = ts3lib.requestChannelUnsubscribeAll(schid)
            if not error == ts3defines.ERROR_ok: raise Exception("Error in requestChannelUnsubscribeAll")
        except:
            (error, clist) = ts3lib.getChannelList(schid)
            ts3lib.requestChannelUnsubscribe(schid, clist)

    def subscribeOpen(self, schid=None):
        if not schid: schid = self.schid
        (error, clist) = ts3lib.getChannelList(schid)
        tosub = []
        for c in clist:
            if not isPassworded(schid, c) and not isPermanent(schid, c) and not isSemiPermanent(schid, c) and not isMusicChannel(schid, c) and isBlacklisted(schid, c):
                tosub.append(c) #clist.remove(c)
        err = ts3lib.requestChannelSubscribe(schid, tosub)
        ts3lib.printMessageToCurrentTab("c: {} err: {}".format(tosub, err))
        self.onlyOpen = True

    def subscribeOpenPW(self, schid=None):
        if not schid: schid = self.schid
        (error, clist) = ts3lib.getChannelList(schid)
        tosub = []
        for c in clist:
            if not isPermanent(schid, c) and not isSemiPermanent(schid, c) and not isMusicChannel(schid, c) and not isBlacklisted(schid, c) and isPWInName(schid, c):
                tosub.append(c) #clist.remove(c)
        err = ts3lib.requestChannelSubscribe(schid, tosub)
        ts3lib.printMessageToCurrentTab("c: {} err: {}".format(tosub, err))
        self.onlyOpen = False

    def onNewChannelCreatedEvent(self, schid, channelID, channelParentID, invokerID, invokerName, invokerUniqueIdentiﬁer):
        if not self.subscribeOpen: return False
        self.subscribe(schid, channelID)

    def onUpdateChannelEditedEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentiﬁer):
        if not self.subscribeOpen: return False
        self.subscribe(schid, channelID)

    def subscribe(self, schid, cid):
        (error, subscribed) = ts3lib.getChannelVariableAsInt(schid, cid, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_ARE_SUBSCRIBED)
        if self.debug:
            ts3lib.printMessageToCurrentTab("==== #{0} ====".format(cid))
            ts3lib.printMessageToCurrentTab("Passworded: {0}".format(isPassworded(schid, cid)))
            ts3lib.printMessageToCurrentTab("PWInName: {0}".format(isPWInName(schid, cid)))
            ts3lib.printMessageToCurrentTab("Blacklisted: {0}".format(isBlacklisted(schid, cid)))
            ts3lib.printMessageToCurrentTab("MusicChannel: {0}".format(isMusicChannel(schid, cid)))
            ts3lib.printMessageToCurrentTab("==== #{0} ====".format(cid))
        if isPassworded(schid, cid) and isPWInName(schid, cid):
            if not subscribed:
                ts3lib.requestChannelSubscribe(schid, [cid])
        elif not isPassworded(schid, cid) and not isBlacklisted(schid, cid) and not isMusicChannel(schid, cid):
            if not subscribed:
                ts3lib.requestChannelSubscribe(schid, [cid])
        elif (isPassworded(schid, cid) and not isPassworded(schid, cid)) or isBlacklisted(schid, cid) or isMusicChannel(schid, cid):
            if subscribed:
                ts3lib.requestChannelUnsubscribe(schid, [cid])

