# coding=utf8
from ts3plugin import ts3plugin, PluginHost
from bluscream import timestamp
from datetime import timedelta
from PythonQt.QtCore import QTimer
import ts3defines, ts3lib, re

class silentError(ts3plugin):
    name = "Anti Flood"
    apiVersion = 21
    requestAutoload = False
    version = "1"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    regex = r"^retry in (\d+)ms$"
    timers = []

    def __init__(self):
        self.regex = re.compile(self.regex)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if error == ts3defines.ERROR_client_is_flooding:
            # print(self.name,"onServerErrorEvent", schid, errorMessage, error, returnCode, extraMessage)
            wait = int(self.regex.match(extraMessage).group(1))
            timer = QTimer
            self.timers.append((schid, wait, timer))
            timer.singleShot(wait, self.floodOver)
            d = timedelta(milliseconds=wait)
            ts3lib.printMessage(schid, "{} [color=red]Remaining Time: [b]{}[/b]".format(self.name, str(d)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)

    def floodOver(self):
        cur = self.timers.pop(0)
        for timer in self.timers:
            if timer[0] == cur[0]: return
        ts3lib.printMessage(cur[0], "{} [color=green][b]expired!".format(self.name), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)