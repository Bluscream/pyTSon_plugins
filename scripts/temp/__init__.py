from ts3plugin import ts3plugin
import ts3lib, ts3defines

class testplugin(ts3plugin):
    name = "hotkeytest"
    requestAutoload = True
    version = "1.0"
    apiVersion = 21
    author = "Timo"
    description = "This is a testplugin"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = ""
    menuItems = []#[(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "text", "icon.png")]
    hotkeys = [("hotkeytest", "description")]#[("keyword", "description")]

    def __init__(self):
        ts3lib.printMessageToCurrentTab("Yay, we are running!")

    def configure(self, qParentWidget):
        ts3lib.printMessageToCurrentTab("configure!")
        ts3lib.requestHotkeyInputDialog("hotkeytest", True)

    def stop(self):
        ts3lib.printMessageToCurrentTab("Oh no, we were stopped :(")

    def onHotkeyRecordedEvent(self, keyword, key):
        ts3lib.printMessageToCurrentTab("Recorded")

    def onHotkeyEvent(self, keyword):
        ts3lib.printMessageToCurrentTab("YEAHHHHH!!!!!")