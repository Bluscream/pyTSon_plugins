from ts3plugin import ts3plugin, PluginHost
from pytsonui import setupUi, getValues, ValueType
from PythonQt.QtGui import QDialog, QInputDialog, QLineEdit
from os import path
from configparser import ConfigParser
import ts3, ts3defines

class cfgDialog(ts3plugin):
    name = "Config Dialog Examples"
    apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Just to show some ways to implement a Config Dialog using ConfigParser and Qt.\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    ini = path.join(ts3.getPluginPath(), "pyTSon", "scripts", "cfgDialog.ini")
    cfg = ConfigParser()

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = { "Example string": "Hello World :)" }
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)

    def configDialogClosed(self, r, vals):
        # Start getValues method +
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
        # End getValues method +

    def configure(self, qParentWidget):
        try:
            # Start QDialog method +
            if not self.dlg:
                self.dlg = SettingsDialog(self)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
            # End QDialog method -
            # Start getValues method +
            d = dict()
            d['api'] = (ValueType.string, "Example String:", self.cfg['general']['example string'], None, 1)
            widgets = getValues(None, self.name+" Settings", d, self.configDialogClosed)
            # End getValues method -
            # Start QInputDialog method +
            result = QInputDialog.getText(qParentWidget, self.name+" Settings", "Example String:", QLineEdit.Normal, self.cfg['general']['example string'])
            if not result: return
            self.cfg.set('general', 'api', result)
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
            # End QInputDialog method -
        except:
            from traceback import format_exc;logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

class SettingsDialog(QDialog):
    # Start QDialog method +
    def __init__(self, cfgDialog, parent=None):
        super(QDialog, self).__init__(parent)
        self.setWindowTitle(self.name+" Settings")
    # End QDialog method +
