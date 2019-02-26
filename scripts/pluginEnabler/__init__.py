import ts3lib, ts3defines # , glob
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp
from os import listdir, path, rename

class pluginEnabler(ts3plugin):
    name = "Plugin Enabler"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []

    def __init__(self):
        self.path = ts3lib.getPluginPath()
        if PluginHost.cfg.getboolean("general", "verbose"):
            ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def menuCreated(self): self.enableAll()
    def enableAll(self):
        for filename in listdir(self.path):
            if not filename.lower().endswith(".off"): continue
            pathname = path.join(self.path, filename)
            newname = filename.replace(".off", "", 1).replace(".OFF", "", 1)
            rename(pathname, path.join(path.dirname(pathname), newname))