from ts3plugin import ts3plugin, PluginHost
from pytsonui import setupUi, getValues, ValueType
from PythonQt.QtCore import QUrl
from PythonQt.QtGui import QDialog, QInputDialog, QLineEdit
from PythonQt.QtNetwork import *
from traceback import format_exc
from os import path
from configparser import ConfigParser
import ts3, ts3defines

class ISPValidator(ts3plugin):
    name = "ISP Validator"
    apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "This script will autokick everyone not using a whitelisted ISP.\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    ini = path.join(ts3.getPluginPath(), "pyTSon", "scripts", "ISPValidator", "settings.ini")
    cfg = ConfigParser()
    requested = 0

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = { "api": "http://ip-api.com/line/{ip}?fields=isp" }
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)

    def configDialogClosed(self, r, vals):
        try:
            if r == QDialog.Accepted:
                for name, val in vals.items():
                    try:
                        if not val == self.cfg.getboolean('general', name):
                            self.cfg.set('general', str(name), str(val))
                    except:
                        ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
                with open(self.ini, 'w') as configfile:
                    self.cfg.write(configfile)
        except:
            ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def configure(self, qParentWidget):
        try:
            result = QInputDialog.getText(qParentWidget, self.name+" Settings", "API:", QLineEdit.Normal, self.cfg['general']['api'])
            if not result: return
            self.cfg.set('general', 'api', result)
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        except:
            ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onClientMoveEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if oldChannelID == 0:
            self.requested = clientID
            ts3.requestConnectionInfo(serverConnectionHandlerID, clientID)

    def onConnectionInfoEvent(self, serverConnectionHandlerID, clientID):
        try:
            if not self.requested == clientID: return
            self.requested = 0
            (error, ip) = ts3.getConnectionVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
            if error == ts3defines.ERROR_ok:
                self.nwm = QNetworkAccessManager()
                self.nwm.connect("finished(QNetworkReply*)", self.onNetworkReply)
                self.nwm.get(QNetworkRequest(QUrl(self.cfg['general']['api'].replace("{ip}",ip))))
        except: ts3.logMessage("%s" % format_exc(), ts3defines.LogLevel.LogLevel_WARNING, "pyTSon.Qt.onNetworkReply", 0)
    def onNetworkReply(self, reply):
        if reply.error() == QNetworkReply.NoError:
            try:
                isp = reply.readAll().data().decode('utf-8')
                ts3.printMessageToCurrentTab(isp)
            except: ts3.logMessage("%s" % format_exc(), ts3defines.LogLevel.LogLevel_WARNING, "pyTSon.Qt.onNetworkReply", 0)
        else: ts3.logMessage("%s" % reply.error(), ts3defines.LogLevel.LogLevel_WARNING, "pyTSon.Qt.onNetworkReply", 0)
        reply.deleteLater()
