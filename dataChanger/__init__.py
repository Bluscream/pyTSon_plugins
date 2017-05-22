import ts3lib, ts3defines
from PythonQt.QtCore import Qt, QTimer
from ts3plugin import ts3plugin
from pytsonui import setupUi
from pytson import getPluginPath
from os import path
from configparser import ConfigParser

class dataChanger(ts3plugin):
    name = "Name Changer"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Changes what you want after a preiod of time."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Nickname changer", "")]
    hotkeys = []
    debug = False
    ini = path.join(getPluginPath(), "scripts", "dataChanger", "settings.ini")
    cfg = ConfigParser()
    dlg = None
    int = 0
    def __init__(self):
        if path.isfile(self.ini): self.cfg.read(self.ini)
        else:
            self.cfg['general'] = { "cfgversion": "1", "debug": "False", "enabled": "True" }
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        ts3lib.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

    def onMenuItemEvent(self, serverConnectionHandlerID, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0:
                timer = QTimer(self);connect(timer, SIGNAL(timeout()), this, SLOT(self.changeName(serverConnectionHandlerID, names[self.i])));timer.start(5000)

    def changeName(self, schid, name=""):
        ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, name)
        ts3lib.flushClientSelfUpdates(schid)
