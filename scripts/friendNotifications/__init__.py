
from ts3plugin import ts3plugin
from bluscream import *
from pytson import getCurrentApiVersion
# from win10toast import ToastNotifier
import ts3defines, ts3lib, ts3client

class friendNotifications(ts3plugin):
    name = "Friend Notifications"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "0.1"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "notify"
    infoTitle = ""
    menuItems = []
    hotkeys = []
    toaster = None # ToastNotifier()

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def processCommand(self, schid, cmd):
        cmd = cmd.split(' ', 1)
        self.toaster.show_toast(cmd[0],
               cmd[1],
               icon_path=None,
               duration=5,
               threaded=True)
        return True