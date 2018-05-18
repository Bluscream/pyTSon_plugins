import ts3lib, ts3defines, configparser, spotipy #, spotilib, spotimeta
from ts3plugin import ts3plugin
from os import path
from pytsonui import setupUi
from PythonQt.QtGui import QDialog, QInputDialog, QMessageBox, QWidget, QListWidgetItem
from PythonQt.QtCore import Qt, QTimer
from bluscream import timestamp


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
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Now Playing", "")]
    hotkeys = []
    ini = path.join(ts3lib.getConfigPath(), "plugins", "pyTSon", "scripts", "nowPlaying", "settings.ini")
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    timer = None
    schid = 0
    prefix = ""
    suffix = ""
    interval = 10000
    enabled = False

    def __init__(self):
        self.dlg = None
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = { "Debug": "False" }
            self.cfg['nowplaying'] = { "client_nickname": "{title}" }
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        # self.timer.timeout.connect(self.tick)
        if self.cfg.getboolean('general', 'Debug'):
            ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if not self.enabled: return
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.schid = schid;self.timer.start(self.interval)
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            self.schid = 0;self.timer.stop()

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            if self.timer is None:
                self.timer = QTimer()
                self.timer.timeout.connect(self.tick)
            if self.timer.isActive():
                self.timer.timeout.disconnect(self.tick)
                self.timer.stop()
                self.timer = None
                del self.timer
                ts3lib.printMessageToCurrentTab('Timer stopped!')
            else:
                self.timer.start(self.interval)
                ts3lib.printMessageToCurrentTab('Timer started!')
            self.enabled = not self.enabled
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.toggle))

    def buildString(self, value):
        return "{0}{1}{2}".format(self.prefix, value.replace('{title}',spotilib.song()).replace('{artist}',spotilib.artist()).replace('{artists}',spotimeta.artists()), self.suffix)

    def getString(self, value):
        return self.cfg.get('nowplaying', value)

    def tick(self):
        if self.getString('client_nickname') != "":
            ts3lib.setClientSelfVariableAsString(self.schid, ts3defines.ClientProperties.CLIENT_NICKNAME, self.buildString(self.getString('client_nickname')))
            ts3lib.flushClientSelfUpdates(self.schid)

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

class SettingsDialog(QDialog):
    def __init__(self, plugin, parent=None):
        super(QDialog, self).__init__(parent)
        setupUi(self, path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "nowPlaying", "settings.ui"))
        self.setWindowTitle("Now Playing Settings")