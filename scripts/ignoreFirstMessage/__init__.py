import ts3lib, ts3defines
from base64 import b64encode
from os import path
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp, getContactStatus, ContactStatus

class ignoreFirstMessage(ts3plugin):
    name = "Ignore First Message"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Ignores first private message from users."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    enabled = True

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        self.enabled = not self.enabled

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if ffIgnored: return False
        if targetMode != ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT: return False
        err, ownID = ts3lib.getClientID(schid)
        if fromID == ownID: return False
        err, uid = ts3lib.getClientVariable(schid, fromID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if getContactStatus(uid) == ContactStatus.FRIEND: return False
        uid_encoded = b64encode(uid.encode()).decode()
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        suid_encoded = b64encode(suid.encode()).decode()
        _path = path.join(ts3lib.getConfigPath(), "chats", suid_encoded, "clients", uid_encoded)
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.name,">","path:", _path)
        if path.exists("{}.html".format(_path)): return False
        if path.exists("{}.txt".format(_path)): return False
        return True
