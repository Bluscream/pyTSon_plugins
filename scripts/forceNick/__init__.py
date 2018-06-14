import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from bluscream import timestamp, inputBox

class forceNick(ts3plugin):
    name = "Force Nickname"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, "scripts/%s/change_nickname.svg"%__name__)]
    nickname = ""

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if self.nickname != "":
            self.nickname = ""
            return
        nickname = inputBox(self.name, "Forced nickname:")
        if nickname: self.nickname = nickname

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        if not self.nickname: return
        ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, self.nickname)
        ts3lib.flushClientSelfUpdates(schid)