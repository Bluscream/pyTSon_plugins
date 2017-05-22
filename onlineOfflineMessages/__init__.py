from datetime import datetime
from os import path
from PythonQt.QtGui import QDialog
from PythonQt.QtCore import Qt
from ts3plugin import ts3plugin
from pytsonui import setupUi
import ts3defines, ts3lib

class onlineOfflineMessages(ts3plugin):
    name = "Online Offline Messages"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Gives you the ability to send offline messages to online users."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    debug = False
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Send Offline Message", "")]
    dlg = None

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT and menuItemID == 0:
            try:
                (error, uid) = ts3lib.getClientVariableAsString(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                (error, name) = ts3lib.getClientVariableAsString(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_NICKNAME)
                if not self.dlg: self.dlg = MessageDialog(schid, uid, name)
                self.dlg.show()
                self.dlg.raise_()
                self.dlg.activateWindow()
            except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

class MessageDialog(QDialog):
    def __init__(self, schid, uid, name, parent=None):
        try:
            self.schid = schid;self.uid = uid;self.name = name
            super(QDialog, self).__init__(parent)
            setupUi(self, path.join(pytson.getPluginPath(), "scripts", "onlineOfflineMessages", "message.ui"))
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Offline Message to {0}".format(name))
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_send_clicked(self):
        try:
            ts3lib.requestMessageAdd(self.schid, self.uid, self.subject.text, self.message.toPlainText())
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_cancel_clicked(self): self.close()
