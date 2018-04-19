from ts3plugin import ts3plugin
from datetime import datetime
from urllib.parse import quote as urlencode
from bluscream import timestamp, sendCommand
from traceback import format_exc
import ts3defines, ts3lib

class rawCMD(ts3plugin):
    name = "CMD Sender"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Makes it easier to manually inject TS3Hook cmds."
    offersConfigure = False
    commandKeyword = "raw"
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = False

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def processCommand(self, schid, cmd):
        try:
            sendCommand(self.name, cmd[1:], schid, False, cmd[0])
            return True
        except:
            ts3lib.printMessageToCurrentTab("Syntax: [b]/py {} <cmd>".format(self.commandKeyword))
            ts3lib.logMessage("Error while processing \"{}\"\n{}".format(cmd, format_exc()), ts3defines.LogLevel.LogLevel_WARNING, self.name, schid)