from ts3plugin import ts3plugin, PluginHost
from ts3 import logMessage, getPluginPath
from os import path
from configparser import ConfigParser
import ts3defines
from PythonQt.QtGui import *
from PythonQt.QtCore import *

class settings(ts3plugin):
    name = "Extended Settings"
    apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Features:\n\n-Toggle Hostbanner\n-Toggle Hostmessage\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    ini = path.join(getPluginPath(), "pyTSon", "scripts", "settings", "settings.ini")
    config = ConfigParser()

    def __init__(self):
        if path.isfile(self.ini):
            self.config.read(self.ini)
        else:
            self.config['general'] = { "hostbanner": "True", "hostmessage": "True" }
            with open(self.ini, 'w') as configfile:
                self.config.write(configfile)
        logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)

    def configDialogClosed(self, r, vals):
        try:
            if r == QDialog.Accepted:
                for name, val in vals.items():
                    try:
                        if not val == self.cfg.getboolean('general', name):
                            self.cfg.set('general', str(name), str(val))
                    except:
                        from traceback import format_exc;logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
                with open(self.ini, 'w') as configfile:
                    self.cfg.write(configfile)
        except:
            from traceback import format_exc;logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def configure(self, qParentWidget):
        try:
            if not self.dlg:
                self.dlg = SettingsDialog(self)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
        except:
            from traceback import format_exc
            logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
