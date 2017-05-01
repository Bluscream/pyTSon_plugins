import ts3lib as ts3
from ts3plugin import ts3plugin, PluginHost
import ts3defines
from PythonQt.QtGui import *
from PythonQt.QtCore import *

class discordify(ts3plugin):
    name = "Discordify"
    import pytson;apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Discordify your Teamspeak :)\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []

    def __init__(self):
        i = QApplication.instance()
        p = QIcon(ts3.getPluginPath()+"pyTSon/scripts/discordify/icon.png")
        for item in i.allWidgets():
            try: item.setWindowIcon(p)
            except: pass
            try:
                t = item.windowTitle.replace("TeamSpeak 3", "")
                if t and not "Discord - " in t:
                    item.setWindowTitle("Discord - " + t)
            except: pass
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
