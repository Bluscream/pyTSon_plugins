from ts3plugin import ts3plugin, PluginHost
from ts3 import logMessage, getPluginPath, printMessageToCurrentTab
from pytsonui import ValueType, getValues
from os import path
from configparser import ConfigParser
import ts3defines
from PythonQt.QtGui import *
from PythonQt.QtCore import *

class settings(ts3plugin):
    name = "Extended Settings"
    apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Features:\n\n-Toggle Hostbanners\n-Toggle Hostmessages\n Toggle Hostbuttons\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    ini = path.join(getPluginPath(), "pyTSon", "scripts", "settings", "settings.ini")
    cfg = ConfigParser()
    dlg = None

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = { "hide hostbanners": "False", "hide hostmessages": "False", "hide hostbuttons": "False" }
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        self.applySettings()
        logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)

    def applySettings(self):
        if self.cfg.getboolean('general','hide hostbuttons'):
            try: self.grabWidget('HosterButton').styleSheet = 'margin:-9999px !important;'
            except: pass
        if self.cfg.getboolean('general','hide hostbanners'):
            try: self.grabWidget('Banner',True).hide()
            except: pass
        if self.cfg.getboolean('general','hide hostmessages'):
            try:
                hostMessage = self.grabWidget('MsgDialog')
                if not hostMessage == None and hostMessage == self.grabWidget('MsgDialog',True):
                    hostMessage.hide();hostMessage.close();hostMessage.delete()
            except: pass

    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHING: self.applySettings()

    def onServerUpdatedEvent(self, serverConnectionHandlerID): self.applySettings()

    def grabWidget(self, objName, byClass=False):
        for widget in QApplication.instance().allWidgets():
            try:
                if byClass and widget.className() == objName: return widget
                elif widget.objectName == objName: return widget
            except: from traceback import format_exc;logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def configDialogClosed(self, r, vals):
        try:
            if r == QDialog.Accepted:
                for n, v in vals.items():
                    try:
                        if not v == self.cfg.getboolean('general', n):
                            self.cfg.set('general', n, str(v))
                    except: from traceback import format_exc;logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
                with open(self.ini, 'w') as configfile:
                    self.cfg.write(configfile)
        except: from traceback import format_exc;logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def configure(self, qParentWidget):
        try:
            d = dict()
            for n, v in self.cfg['general'].items():
                d[n] = (ValueType.boolean, n.title(), self.cfg.getboolean('general', n), None, None)
            getValues(qParentWidget, self.name, d, self.configDialogClosed)
        except: from traceback import format_exc;logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
