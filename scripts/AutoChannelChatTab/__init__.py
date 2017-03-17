from ts3plugin import ts3plugin
import ts3defines

from PythonQt.QtGui import *
from PythonQt.QtCore import *

class autoChannelChatTab(ts3plugin):
    name = "AutoChannelChatTab"
    apiVersion = 21
    requestAutoload = True
    version = "1.0.1"
    author = "Thomas \"PLuS\" Pathmann"
    description = "Automatically activates the channel chat (tabindex 1, so if you change order, it won't work as expected) tab when the server connection tab is changed"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = False
    toggle = True

    def __init__(self):
        self.chattab = None
        self.retrieveWidgets()

    def retrieveWidgets(self):
        process = False

        if not hasattr(self, "main"):
            qapp = QApplication.instance()

            for w in qapp.topLevelWidgets():
                if "MainWindow" in str(type(w)):
                    self.main = w
                    process = True
        else:
            process = True

        if process and not hasattr(self, "splitter"):
            process = False
            for c in self.main.children():
                if type(c) is QSplitter:
                    self.splitter = c
                    process = True
                    break

        if process and (not hasattr(self, "chat")):
            process = False
            for c in self.splitter.children():
                if c.objectName == "MainWindowChatWidget":
                    self.chat = c
                    process = True

        if process and not self.chattab:
            for c in self.chat.children():
                if c.objectName == "ChatTabWidget":
                    self.chattab = c
                    return

        if not process:
            #it's possible that this plugin is started before the client's UI is loaded
            QTimer.singleShot(300, self.retrieveWidgets)

    def activateChannelChat(self):
        if self.chattab:
            if self.chattab.count < 2:
                #it's a new schid, so in most cases chattabs not yet available
                QTimer.singleShot(300, lambda: self.onConnectStatusChangeEvent(schid))
            else:
                self.chattab.setCurrentIndex(1)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.activateChannelChat()

