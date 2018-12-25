from ts3plugin import ts3plugin, PluginHost
from bluscream import *
from pytson import getPluginPath, getCurrentApiVersion
from traceback import format_exc
import ts3defines, ts3lib, ts3client

class avatarScanner(ts3plugin):
    name = "Scan Avatars"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1"
    author = "Bluscream"
    description = "Let's you scan the subscribed channels for users that have an avatar set"
    offersConfigure = False
    commandKeyword = "avatar"
    infoTitle = None
    menuItems = [] # [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, "")]
    hotkeys = []

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def processCommand(self, schid, command): self.printAvatarUsers(schid); return True

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0: self.printAvatarUsers(schid)

    def printAvatarUsers(self, schid):
        (err, clist) = ts3lib.getClientList(schid)
        msg = []
        for c in clist:
            (err, avatar) = ts3lib.getClientVariable(schid, c, ts3defines.ClientPropertiesRare.CLIENT_FLAG_AVATAR)
            if not avatar or avatar.strip() == "": continue
            msg.append("{}: {}".format(clientURL(schid, c), avatar))
        ts3lib.printMessageToCurrentTab("{}[u]Online users with avatars[/u]: [b]{}[/b]".format(timestamp(), len(msg)))
        i = 1
        for m in msg: ts3lib.printMessageToCurrentTab("{} {}".format(i, m)); i += 1
