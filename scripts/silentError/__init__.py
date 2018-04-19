from ts3plugin import ts3plugin, PluginHost
from bluscream import timestamp
import ts3defines, ts3lib

class silentError(ts3plugin):
    name = "Silent Errors"
    apiVersion = 21
    requestAutoload = False
    version = "1"
    author = "Bluscream"
    description = "Silences TeaSpeak's \"not implemented\" errors"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        return True

