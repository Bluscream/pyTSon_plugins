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
    commandKeyword = None
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, "")]
    hotkeys = []

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        (err, clist) = ts3lib.getClientList(schid)
        msg = []
        for c in clist:
            (err, mdata) = ts3lib.getClientVariable(schid, c, ts3defines.ClientProperties.CLIENT_META_DATA)
            if mdata and mdata.strip() != "":
                mdata = (mdata[:100].replace("\n", "\\n"))
                msg.append("{}: {}".format(clientURL(schid, c), mdata))
        ts3lib.printMessageToCurrentTab("{}[u]Online users with metadata[/u]: [b]{}[/b]".format(timestamp(), len(msg)))
        try: msg.sort(key=lambda s: s.split(": ")[1])
        except: pass
        i = 1
        for m in msg: ts3lib.printMessageToCurrentTab("{} {}".format(i, m)); i += 1