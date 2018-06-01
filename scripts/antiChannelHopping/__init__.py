import ts3lib, ts3defines
from time import time
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp, sendCommand, getAddons, inputInt, calculateInterval, AntiFloodPoints, intList, parseTime, getContactStatus, ContactStatus, varname

class antiChannelHopping(ts3plugin):
    name = "Anti Channel Hopping"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "( .) ( .)"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    clients = {}
    maxviolations = 2
    bancgid = 12
    modcgids = [10,11]

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        (err, ownID) = ts3lib.getClientID(schid)
        if clid == ownID: return #(err, clids) = ts3lib.getChannelClientList(schid, newChannelID)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if newChannelID == 0:
            if clid in self.clients: del self.clients[clid]
        if ownCID != newChannelID: return
        (err, owncgid) = ts3lib.getClientVariable(schid, ownID, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
        if owncgid in self.modcgids: return
        (err, cgid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
        (err, dcgid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
        if cgid != dcgid: return
        if clid in self.clients:
            violations = self.clients[clid]
            if len(violations) > self.maxviolations:
                if len(violations) > self.maxviolations+3: del self.clients[clid][0]
                if violations[-1] < violations[-3]+3:
                    (err, dbid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                    ts3lib.requestSetClientChannelGroup(schid, [self.bancgid], [ownCID], [dbid])
                    return
            self.clients[clid].append(time())
        else:
            self.clients[clid] = []
