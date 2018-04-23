import ts3lib, ts3defines
from random import randint
from datetime import datetime
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from pytson import getCurrentApiVersion
from bluscream import timestamp, sendCommand, getAddons

class teaspeakBot(ts3plugin):
    name = "TeaSpeak Bot"
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
    servers = {
        "siAK/P4hf0ntXOfy3TaW3GwkoPA=": [15,18,23]
    }

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onNewChannelCreatedEvent(self, schid, cid, channelParentID, clid, invokerName, invokerUniqueIdentifier):
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if not suid in self.servers: return
        (err, sgids) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        if not set(sgids).isdisjoint(self.servers[suid]): return
        (err, perm) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PERMANENT)
        # (err, semi) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_SEMI_PERMANENT)
        if not perm: return
        ts3lib.setChannelVariableAsInt(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PERMANENT, 0)
        ts3lib.flushChannelUpdates(schid, cid)

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if hasattr(self, "retcode") and returnCode == self.retcode: self.retcode = ""; return True
