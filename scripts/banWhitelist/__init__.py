import ts3defines, ts3lib, pytson
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from bluscream import saveCfg, loadCfg, timestamp, intList, getScriptPath
from configparser import ConfigParser

class banWhitelist(ts3plugin):
    path = getScriptPath(__name__)
    name = "Ban Whitelist"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Automatically removes whitelisted IPs from the banlist"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    suid = "9lBVIDJRSSgAGy+cWJgNlUQRd64="
    requested = 0
    whitelist = []

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def onClientBanFromServerEvent(self, schid, clid, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, time, kickMessage):
        active = PluginHost.active
        if not "Custom Ban" in active: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.suid: return
        self.requested = schid
        self.whitelist = active["Custom Ban"].whitelist
        if len(self.whitelist) < 1: return
        ts3lib.requestBanList(schid)

    def onBanListEvent(self, schid, banid, ip, name, uid, creationTime, durationTime, invokerName, invokercldbid, invokeruid, reason, numberOfEnforcements, lastNickName):
        if self.requested != schid: return
        if not ip in self.whitelist: return
        ts3lib.printMessageToCurrentTab("{}: [color=red]Unbanning whitelisted IP [b]{}".format(self.name, ip))
        ts3lib.bandel(schid, banid)