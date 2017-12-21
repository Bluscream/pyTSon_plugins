from os import path
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtGui import QWidget
from PythonQt.QtCore import Qt
from pytsonui import setupUi
import ts3lib, ts3defines, datetime, pytson

def my_decorator(func):
    def wrapped_func(*args,**kwargs):
        return func("I've been decorated!",*args,**kwargs)
    return wrapped_func
# print = my_decorator(print)

class queryConsole(ts3plugin):
    name = "TS3 Query Console"
    apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Adds a query console to your Teamspeak 3 Client.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Show Query Console", "")]
    hotkeys = []
    debug = False
    toggle = True
    dlg = None

    def __init__(self):
        ts3lib.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug:
            ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            if not self.dlg: self.dlg = QueryConsole()
            self.dlg.show();self.dlg.raise_();self.dlg.activateWindow()

class QueryConsole(QWidget):
    def __init__(self, parent=None):
        try:
            super(QWidget, self).__init__(parent)
            setupUi(self, path.join(pytson.getPluginPath(), "scripts", "queryConsole", "console.ui"))
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Query Console")
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_btn_send_clicked(self):
        try: ts3lib.requestMessageAdd(self.schid, uid, self.subject.text, self.message.toPlainText())
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_btn_connect_clicked(self): self.close()
