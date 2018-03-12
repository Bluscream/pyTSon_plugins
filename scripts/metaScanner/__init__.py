from ts3plugin import ts3plugin, PluginHost
from bluscream import *
from pytson import getPluginPath, getCurrentApiVersion
from traceback import format_exc
import ts3defines, ts3lib, ts3client

class metaScanner(ts3plugin):
    name = "Scan Meta Data"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1"
    author = "Bluscream"
    description = "Let's you scan the subscribed channels for users that have metaData set"
    offersConfigure = False
    commandKeyword = "meta"
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, "")]
    hotkeys = []

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def processCommand(self, schid, command): self.printMetaUsers(schid); return True

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0: self.printMetaUsers(schid)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if oldChannelID != 0: return
        (err, mdata) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_META_DATA)
        if not mdata or mdata.strip() == "": return
        ts3lib.printMessage(schid, "{} {}'s Metadata: {}".format(timestamp(), clientURL(schid, clientID), mdata), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)

    def printMetaUsers(self, schid):
        (err, clist) = ts3lib.getClientList(schid)
        msg = []
        for c in clist:
            (err, mdata) = ts3lib.getClientVariable(schid, c, ts3defines.ClientProperties.CLIENT_META_DATA)
            if not mdata or mdata.strip() == "": continue
            mdata = (mdata[:100].replace("\n", "\\n"))
            msg.append("{}: {}".format(clientURL(schid, c), mdata))
        ts3lib.printMessageToCurrentTab("{}[u]Online users with metadata[/u]: [b]{}[/b]".format(timestamp(), len(msg)))
        try: msg.sort(key=lambda s: s.split(": ")[1])
        except: pass
        i = 1
        for m in msg: ts3lib.printMessageToCurrentTab("{} {}".format(i, m)); i += 1