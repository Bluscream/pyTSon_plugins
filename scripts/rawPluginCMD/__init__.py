from ts3plugin import ts3plugin
from datetime import datetime
from urllib.parse import quote as urlencode
import ts3defines, ts3lib, _ts3lib

class rawPluginCMD(ts3plugin):
    name = "Raw Plugin CMD sender / viewer"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Ability to view incoming plugincmds and send own ones via chat commands."
    offersConfigure = False
    commandKeyword = "rawcmd"
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = False

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def clientURL(self, schid=None, clid=1, uid=None, nickname=None, encodednick=None):
        if schid == None:
            try: schid = ts3lib.getCurrentServerConnectionHandlerID()
            except: pass
        if uid == None:
            try: (error, uid) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            except: pass
        if nickname == None:
            try: (error, nickname) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
            except: nickname = uid
        if encodednick == None:
            try: encodednick = urlencode(nickname)
            except: pass
        return "[url=client://{0}/{1}~{2}]{3}[/url]".format(clid, uid, encodednick, nickname)

    def processCommand(self, schid, cmd):
        cmd = cmd.split(' ', 1)
        targetmode = cmd[0].lower()
        target = []
        command = cmd[1]
        if targetmode in ["chan", "channel", "0"]:
            targetmode = ts3defines.PluginTargetMode.PluginCommandTarget_CURRENT_CHANNEL
        elif targetmode in ["serv", "server", "1"]:
            targetmode = ts3defines.PluginTargetMode.PluginCommandTarget_SERVER
        elif targetmode in ["cli", "client", "2"]:
            targetmode = ts3defines.PluginTargetMode.PluginCommandTarget_CLIENT
            _cmd = cmd[1].split(' ', 1)
            target = [int(_cmd[0])]
            command = _cmd[1]
        elif targetmode in ["chansub", "channelsubscribed", "3"]:
            targetmode = ts3defines.PluginTargetMode.PluginCommandTarget_CURRENT_CHANNEL_SUBSCRIBED_CLIENTS
        _ts3lib.sendPluginCommand(schid, command, targetmode, target)
        return True