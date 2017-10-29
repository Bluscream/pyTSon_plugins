import ts3lib, ts3defines, datetime
from ts3plugin import ts3plugin
from pytson import getPluginPath
from os import path
from base64 import b64encode
from PythonQt.QtCore import QTimer


class autoEncode(ts3plugin):
    name = "Auto Encode"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle "+name, "")]
    hotkeys = []
    debug = False
    enabled = True

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0: self.enabled = not self.enabled

    def onClientSelfVariableUpdateEvent(self, schid, flag, oldValue, newValue):
        if flag in [ts3defines.ClientProperties.CLIENT_NICKNAME, ts3defines.ClientPropertiesRare.CLIENT_AWAY_MESSAGE]:
            if newValue.endswith("="): return
            encoded = b64encode(newValue.encode('ascii')).decode('utf-8')
            if not encoded.endswith("="): encoded + "="
            ts3lib.setClientSelfVariableAsString(schid, flag, encoded)
            ts3lib.flushClientSelfUpdates(schid)