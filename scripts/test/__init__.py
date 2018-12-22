from ts3plugin import ts3plugin

import ts3lib, ts3defines

class testplugin(ts3plugin):
    name = "test"
    requestAutoload = False
    version = "1.0"
    apiVersion = 21
    author = "Splamy"
    description = "This is a testplugin"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = ""
    menuItems = []#[(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "text", "icon.png")]
    hotkeys = []#[("keyword", "description")]

    def __init__(self):
        ts3lib.printMessageToCurrentTab("Yay, we are running!")

    def onPacketIn(self, msg, schid):
        print("py onPacketIn")
        # ts3lib.printMessageToCurrentTab(msg)
        return False, msg

    def onPacketOut(self, msg, schid):
        print("py onPacketOut")
        # ts3lib.printMessageToCurrentTab(msg)
        return False, msg