from ts3plugin import ts3plugin, PluginHost
import ts3lib, ts3defines, configparser, os.path
from PythonQt.QtGui import QDialog, QInputDialog, QMessageBox, QWidget, QListWidgetItem
from PythonQt.QtCore import Qt
from pytsonui import setupUi
from collections import OrderedDict
from inspect import getmembers
from datetime import datetime

class nowPlaying(ts3plugin):
    name = "Now Playing"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Now playing plugin in pyTSon"
    offersConfigure = True
    commandKeyword = "info"
    infoTitle = "[b]"+name+":[/b]"
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Set Meta Data", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Set Avatar Flag", "")]
    hotkeys = []
    ini = os.path.join(ts3lib.getConfigPath(), "plugins", "pyTSon", "scripts", "info", "settings.ini")
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    runs = 0

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        self.dlg = None
        if os.path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = { "Debug": "False", "Colored": "False", "Autorequest Server Variables": "False", "Autorequest Client Variables": "False" }
            self.cfg.add_section('VirtualServerProperties');self.cfg.add_section('VirtualServerPropertiesRare');
            self.cfg.add_section('ChannelProperties');self.cfg.add_section('ChannelPropertiesRare');
            self.cfg.add_section('ClientProperties');self.cfg.add_section('ClientPropertiesRare');
            self.cfg.add_section('ConnectionProperties');self.cfg.add_section('ConnectionPropertiesRare')
            self.cfg.set("VirtualServerProperties", "LAST_REQUESTED", "True");self.cfg.set("VirtualServerProperties", "TYPE", "True")
            for name, value in getmembers(ts3defines.VirtualServerProperties):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER'):
                    self.cfg.set("VirtualServerProperties", name, "False")
            for name, value in getmembers(ts3defines.VirtualServerPropertiesRare):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER_RARE'):
                    self.cfg.set("VirtualServerPropertiesRare", name, "False")
            self.cfg.set("ChannelProperties", "LAST_REQUESTED", "True");self.cfg.set("ChannelProperties", "TYPE", "True");self.cfg.set("ChannelProperties", "ID", "True")
            for name, value in getmembers(ts3defines.ChannelProperties):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER'):
                    self.cfg.set("ChannelProperties", name, "False")
            for name, value in getmembers(ts3defines.ChannelPropertiesRare):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER_RARE'):
                    self.cfg.set("ChannelPropertiesRare", name, "False")
            self.cfg.set("ClientProperties", "LAST_REQUESTED", "True");self.cfg.set("ClientProperties", "TYPE", "True");self.cfg.set("ClientProperties", "ID", "True")
            for name, value in getmembers(ts3defines.ClientProperties):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER'):
                    self.cfg.set("ClientProperties", name, "False")
            for name, value in getmembers(ts3defines.ClientPropertiesRare):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER_RARE'):
                    self.cfg.set("ClientPropertiesRare", name, "False")
            for name, value in getmembers(ts3defines.ConnectionProperties):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER'):
                    self.cfg.set("ConnectionProperties", name, "False")
            for name, value in getmembers(ts3defines.ConnectionPropertiesRare):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER_RARE'):
                    self.cfg.set('ConnectionPropertiesRare', name, 'False')
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)

        if self.cfg.getboolean('general', 'Debug'):
            ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def configDialogClosed(self, r, vals):
        try:
            ts3lib.printMessageToCurrentTab("vals: "+str(vals))
            if r == QDialog.Accepted:
                for name, val in vals.items():
                    try:
                        if not val == self.cfg.getboolean('general', name):
                            self.cfg.set('general', str(name), str(val))
                    except:
                        from traceback import format_exc
                        ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
                with open(self.ini, 'w') as configfile:
                    self.cfg.write(configfile)
        except:
            from traceback import format_exc
            ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def configure(self, qParentWidget):
        try:
            if not self.dlg:
                self.dlg = SettingsDialog(self)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
        except:
            from traceback import format_exc
            ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
