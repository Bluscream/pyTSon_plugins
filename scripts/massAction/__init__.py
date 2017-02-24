__author__ = 'Bluscream'
from ts3plugin import ts3plugin
import datetime, ts3defines, ts3lib

class massAction(ts3plugin):
    name = "Mass Actions"
    apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Gives you the ability to take actions to all users in a channel or the server."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Message all Clients", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Poke all Clients", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "Kick all Clients", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 3, "Ban all Clients", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Message all Clients", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 1, "Poke all Clients", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 2, "Kick all Clients", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 3, "Ban all Clients", "")]
    hotkeys = []
    debug = False

    def __init__(self):
        ts3lib.logMessage(self.name + " script for pyTSon by " + self.author + " loaded from \"" + __file__ + "\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(
            datetime.datetime.now()) + " [color=orange]" + self.name + "[/color] Plugin for pyTSon by [url=https://github.com/" + self.author + "]" + self.author + "[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0:
                error, ownid = ts3lib.getClientID(schid)
                error, ownchan = ts3lib.getChannelOfClient(schid, ownid)
                self.sendMessage(schid, ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL, ownchan)
            elif menuItemID == 1: pass
            elif menuItemID == 2: pass
            elif menuItemID == 3: pass
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL:
            if menuItemID == 0:
                self.sendMessage(schid, ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL, selectedItemID)
            elif menuItemID == 1: pass
            elif menuItemID == 2: pass
            elif menuItemID == 3: pass


    def sendMessage(self, schid, targetMode, toID):
        x = QWidget()
        clipboard = QApplication.clipboard().text();
        _message = QInputDialog.getMultiLineText(x, "Enter long text here", "", clipboard)
        message = [_message[i:i + 1024] for i in range(0, len(_message), 1024)]
        if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL:
            for msg in message:
                error = ts3lib.requestSendChannelTextMsg(schid, msg, toID)
        elif targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT:
            for msg in message:
                error = ts3lib.requestSendPrivateTextMsg(schid, msg, toID)