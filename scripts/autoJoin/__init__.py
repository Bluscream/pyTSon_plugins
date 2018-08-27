import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp, getScriptPath, getChannelPassword

def channelClientCount(schid, channelID):
    (error, clients) = ts3lib.getChannelClientList(schid, channelID)
    if error == ts3defines.ERROR_ok: return len(clients)
    else: return error

def isPermanent(schid, cid):
    (error, permanent) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PERMANENT)
    return bool(permanent)

def isSemiPermanent(schid, cid):
    (error, semipermanent) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_SEMI_PERMANENT)
    return bool(semipermanent)

class autoJoin(ts3plugin):
    path = getScriptPath(__name__)
    name = "Auto Join"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, "")]
    hotkeys = []
    schid = 0
    request_tp = False

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        if schid == self.schid: self.schid = 0; ts3lib.printMessageToCurrentTab("{} > Disabled!".format(self.name))
        else: self.schid = schid; ts3lib.printMessageToCurrentTab("{} > Enabled for tab #{}!".format(self.name,schid))

    def onNewChannelCreatedEvent(self, schid, cid, channelParentID, invokerID, invokerName, invokerUniqueIdentifier):
        if schid != self.schid: print(cid, "schid != self.schid"); return
        (err, ownID) = ts3lib.getClientID(schid)
        if invokerID == ownID: print(cid, "invokerID == ownID"); return
        if isPermanent(schid, cid) or isSemiPermanent(schid, cid): print("isPermanent(schid, cid) or isSemiPermanent(schid, cid)"); return
        (error, maxclients) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        # (error, maxfamilyclients) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_MAXFAMILYCLIENTS)
        if maxclients != -1:
            clients = channelClientCount(schid, cid)
            if clients >= maxclients: print(cid, "clients >= maxclients"); return
        (err, needed_tp) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        if needed_tp >=0:
            (err, ownTP) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_TALK_POWER)
            if int(ownTP) < needed_tp: self.request_tp = True
        (err, pw) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
        if err == ts3defines.ERROR_ok and pw:
            pw = getChannelPassword(schid, cid, False, False, True)
            # ts3lib.verifyChannelPassword(schid, cid, pw, "passwordCracker:manual")
            if not pw: print(cid, "not pw"); return
        ts3lib.requestClientMove(schid, ownID, cid, pw if pw else "123")

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if schid != self.schid: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID != ownID: return
        if not self.request_tp: return
        self.request_tp = False
        ts3lib.requestIsTalker(schid, True, "")