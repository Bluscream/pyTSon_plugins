import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp, getScriptPath, loadCfg
from configparser import ConfigParser
from enum import Enum

class PrintMessageTargetMode(object):
    CURRENT_TAB = 0
    SERVER = 1
    CHANNEL = 2
    CLIENT = 3

class TextMessageTargetMode(object):
    TextMessageTarget_CLIENT = 1
    TextMessageTarget_CHANNEL = 2
    TextMessageTarget_SERVER = 3
    TextMessageTarget_MAX = 4

class PluginMessageTarget(object):
    PLUGIN_MESSAGE_TARGET_SERVER = 0
    PLUGIN_MESSAGE_TARGET_CHANNEL = 1

def printMessage(self, schid, msg, fromID, mode=PrintMessageTargetMode.CURRENT_TAB):
    if mode == PrintMessageTargetMode.CURRENT_TAB: ts3lib.printMessageToCurrentTab(msg)
    else:
        if mode == PrintMessageTargetMode.SERVER:
            pass
            # ts3lib.printMessage(schid, msg, messageTarget)


class antiSpam(ts3plugin):
    path = getScriptPath(__name__)
    name = "Anti Spam"
    apiVersion = 22
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    version = "1.0"
    author = "Bluscream"
    description = ""
    requestAutoload = False
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = []
    ini = "%s/config.ini" % path
    cfg = ConfigParser({
        "messages": {
            "block similar messages": "True",
            "force show ignored messages": "False",
            "block messages longer then": str(ts3defines.TS3_MAX_SIZE_TEXTMESSAGE),
            "whitespace": "strip", # block
            "block messages sent inbetween": "1000",
            "apply to": "1,2,3" # ",".join([ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT,ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL,ts3defines.TextMessageTargetMode.TextMessageTarget_SERVER])
        }
    })
    tabs = {}

    def __init__(self):
        loadCfg(self.ini, self.cfg)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self): del self.tabs

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if self.cfg.getboolean("messages", "force show ignored messages"):
            pass
        if self.cfg.getboolean("messages", "block similar messages"):
            pass

    def onClientPokeEvent(self, schid, fromClientID, pokerName, pokerUID, message, ffIgnored):
        pass

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if newChannelID == 0: self.removeClient(schid, clientID)
    def onClientKickFromServerEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage): self.removeClient(schid, clientID)
    def removeClient(self, schid, clid):
        if not schid in self.tabs: return
        if not clid in self.tabs[schid]: return
        del self.tabs[schid][clid]
    def addClient(self, schid, clid):
        if not schid in self.tabs:
            self.tabs[schid] = {}
        if not clid in self.tabs[schid]:
            self.tabs[schid][clid] = {}