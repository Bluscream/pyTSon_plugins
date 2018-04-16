from ts3plugin import ts3plugin
from datetime import datetime
from urllib.parse import quote as urlencode
from bluscream import timestamp, clientURL
from traceback import format_exc
import ts3defines, ts3lib, _ts3lib

class pluginCMD(ts3plugin):
    name = "Plugin CMD sender / viewer"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Ability to view incoming plugincmds and send own ones via chat commands."
    offersConfigure = False
    commandKeyword = "cmd"
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = False

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def processCommand(self, schid, fullcmd):
        try:
            cmd = fullcmd.split(' ', 1)
            mode = cmd[0].lower()
            _cmd = cmd[1].split(' ', 1)
            targetmode = _cmd[0].lower()
            command = _cmd[1]
            target = []
            if targetmode in ["chan", "channel", "0"]:
                targetmode = ts3defines.PluginTargetMode.PluginCommandTarget_CURRENT_CHANNEL
            elif targetmode in ["serv", "server", "1"]:
                targetmode = ts3defines.PluginTargetMode.PluginCommandTarget_SERVER
            elif targetmode in ["cli", "client", "2"]:
                targetmode = ts3defines.PluginTargetMode.PluginCommandTarget_CLIENT
                _cmd = command[1].split(' ', 1)
                target = [int(_cmd[0])]
                command = _cmd[1]
            elif targetmode in ["chansub", "channelsubscribed", "3"]:
                targetmode = ts3defines.PluginTargetMode.PluginCommandTarget_CURRENT_CHANNEL_SUBSCRIBED_CLIENTS
            if mode in ["raw", "r", "true", "1"]: _ts3lib.sendPluginCommand(schid, command, targetmode, target)
            else: ts3lib.sendPluginCommand(schid, command, targetmode, target)
            return True
        except:
            ts3lib.printMessageToCurrentTab("Syntax: [b]/py {} <raw> <channel,server,channelsubscribed,client <clid>> <cmd>".format(self.commandKeyword))
            ts3lib.logMessage("Error while processing \"{}\"\n{}".format(fullcmd, format_exc()), ts3defines.LogLevel.LogLevel_WARNING, self.name, schid)


    def onPluginCommandEvent(self, schid, clid, pluginCommand):
        ts3lib.printMessageToCurrentTab("onPluginCommandEvent")
        ts3lib.printMessage(schid, "{0} PluginMessage from {1}: {2}".format(timestamp(), clientURL(clid), pluginCommand), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)