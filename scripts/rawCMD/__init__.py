from ts3plugin import ts3plugin
from datetime import datetime
from urllib.parse import quote as urlencode
from bluscream import timestamp, sendCommand
from traceback import format_exc
import ts3defines, ts3lib

class rawCMD(ts3plugin):
    name = "Protocol CMD sender / reciever"
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
    in_strs = ["-", "in", "i"]
    out_strs = ["~", "out", "o"]

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def processCommand(self, schid, cmd):
        try:
            cmd = cmd.split(" ", 1)
            dir_ = cmd[0].lower()
            if dir_ in self.in_strs:
                reverse = True
            elif dir_ in self.out_strs:
                reverse = False
            else: raise(SyntaxError, "Invalid direction: use {} or {}".format(self.in_strs, self.out_strs))
            sendCommand(self.name, cmd[1], schid, False, reverse)
            return True
        except:
            ts3lib.printMessageToCurrentTab("Syntax: [b]/py {} <{}/{}> <cmd>".format(self.commandKeyword, self.in_strs, self.out_strs))
            ts3lib.logMessage("Error while processing \"{}\"\n{}".format(cmd, format_exc()), ts3defines.LogLevel.LogLevel_WARNING, self.name, schid)