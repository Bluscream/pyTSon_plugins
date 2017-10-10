import ts3lib as ts3
from ts3plugin import ts3plugin
# noinspection PyUnresolvedReferences
from PythonQt.QtGui import *
# noinspection PyUnresolvedReferences
from PythonQt.QtCore import *

class discordify(ts3plugin):
    name = "Discordify"

    apiVersion = 22
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
        # noinspection PyUnresolvedReferences
        i = QApplication.instance()
        # noinspection PyUnresolvedReferences
        p = QIcon(ts3.getPluginPath()+"pyTSon/scripts/discordify/icon.png")
        for item in i.allWidgets():
            try: item.setWindowIcon(p)
            except: pass
            try:
                t = item.windowTitle.replace("TeamSpeak 3", "")
                if t and not "Discord - " in t:
                    item.setWindowTitle("Discord - " + t)
            except: pass

