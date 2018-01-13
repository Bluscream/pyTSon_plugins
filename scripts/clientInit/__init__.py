from ts3plugin import ts3plugin
from random import choice, getrandbits
from PythonQt.QtCore import QTimer, Qt
from bluscream import timestamp, sendCommand, calculateInterval, AntiFloodPoints
import ts3defines, ts3lib

class clientInit(ts3plugin):
    name = "Client Init"
    apiVersion = 21
    requestAutoload = True
    version = "1"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [] # [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    debug = True
    requested = False
    clientinit = [
        ("client_nickname", "penis"),
        ("client_version", "3.1.7\s[Build:\s1513163251]"),
        ("client_version_sign", ""),
        ("client_platform", "Windows"),
        ("client_output_muted", "1"),
        ("client_input_hardware", "1"),
        ("client_output_hardware", "1"),
        ("client_default_channel", ""),
        ("client_default_channel_password", ""),
        ("client_server_password", ""),
        ("client_meta_data", ""),
        ("client_key_offset", "30054583"),
        ("client_nickname_phonetic", ""),
        ("client_default_token", ""),
        ("client_badges", "Overwolf=0"),
        ("hwid", "123,456")
    ]

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        pass

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        if schid in self.timers: self.stopTimer(schid)
        else: self.startTimer(schid)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTING:
            sendCommand(self.name, self.buildClientInit())
        elif newStatus == ts3defines.ConnectStatus.STATUS_CONNECTED: pass
        elif newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHING: pass
        elif newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: pass
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED: pass

    def buildClientInit(self):
        cmd = "clientinit"
        for key in self.clientinit:
            cmd += " {}={}".format(key[0], key[1])
        return cmd
