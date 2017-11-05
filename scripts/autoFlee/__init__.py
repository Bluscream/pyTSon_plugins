import ts3lib, ts3defines, configparser
from datetime import datetime
from random import choice
from ts3plugin import ts3plugin
from os import path
from getvalues import getValues, ValueType
from PythonQt.QtCore import QTimer
from PythonQt.QtGui import QDialog


class autoFlee(ts3plugin):
    name = "Auto Flee"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Deny others to move you around."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "AutoFlee", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "AutoFlee", "")]
    hotkeys = []
    config = configparser.ConfigParser()
    cids = []
    clids = []
    ini = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "autoFlee", "cfg", "settings.ini")

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        _class = self.__class__.__bases__[0]
        if path.isfile(self.ini):
            self.config.read(self.ini)
            if not self.config.has_section('general'):
                self.config.add_section('general')
                self.config.set('general', 'enabled', "False")
                self.config.set('general', 'debug', "False")
                self.config.set('general', 'cids', "")
                self.config.set('general', 'clids', "")
        else:
            self.config['general'] = {"enabled": "False", "debug": "False", "cids": "", "clids": "" }
        with open(self.ini, 'w') as configfile:
            self.config.write(configfile)
        self.cids = self.config.get('general', 'cids').split(',')
        # self.clids = self.config.get('general', 'clids').split(',')
        if self.config.getboolean("general", "debug"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def stop(self):
        # for var in ['cids', 'clids']:
            # _var = self.config.get('general', var)
        self.config.set('general', 'cids', ','.join(map(str, self.cids)).replace("'',", ''))
        self.config.set('general', 'clids', ','.join(map(str, self.clids)).replace("'',", ''))
        with open(self.ini, 'w') as configfile:
            self.config.write(configfile)

    def configure(self, qParentWidget):
        try:
            d = dict()
            d['enabled'] = (ValueType.boolean, "Enabled", self.config['general']['enabled'] == "True", None, None)
            d['debug'] = (ValueType.boolean, "Debug", self.config['general']['debug'] == "True", None, None)
            d['cids'] = (ValueType.string, "CIDS:", self.config['general']['cids'], None, 1)
            d['clids'] = (ValueType.string, "CLIDS:", self.config['general']['clids'], None, 1)
            getValues(None, self.name + " Settings", d, self.configDialogClosed)
        except:
            from traceback import format_exc
            try: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon::"+self.name, 0)
            except: print("Error in "+self.name+".configure: "+format_exc())

    def configDialogClosed(self, r, vals):
        if r == QDialog.Accepted:
            self.cfg['general'] = { "enabled": str(vals["enabled"]), "debug": str(vals["debug"]), "cids": vals["debug"], "clids": vals["clids"] }
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            self.config.set("general", "enabled", not self.config.getboolean("general", "enabled"))
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.config.getboolean("general", "enabled")))
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL and menuItemID == 0:
            if str(selectedItemID) in self.cids: self.cids.remove(str(selectedItemID))
            else: self.cids.append(str(selectedItemID))
            ts3lib.printMessageToCurrentTab("{0} {1}> Channels to flee to: {2}".format(self.timestamp(), self.name, self.cids))
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT and menuItemID == 0:
            if selectedItemID in self.clids: self.clids.remove(selectedItemID)
            else: self.clids.append(selectedItemID)
            ts3lib.printMessageToCurrentTab("{0} {1}> Clients to flee from: {2}".format(self.timestamp(), self.name, self.cids))

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.config.getboolean("general", "enabled"): return
        if not str(clientID) in self.clids: return
        (err, ownID) = ts3lib.getClientID(schid)
        if clientID == ownID: return
        (err, ownCID) = ts3lib.getChannelOfClient(schid, clientID)
        if newChannelID != ownCID: return
        chan = 0
        while chan <= 0 or chan == newChannelID:
            chan = choice(self.cids)
        ts3lib.requestClientMove(schid, ownID, chan, "123")