import ts3defines, re, pytson
import ts3lib as ts3
from ts3plugin import ts3plugin
from datetime import datetime
import xml.etree.ElementTree as xml
from getvalues import getValues, ValueType
from configparser import ConfigParser
from os import path
from PythonQt.QtCore import Qt
from PythonQt.QtGui import (QDialog, QWidget, QTableWidgetItem, QHeaderView, QFont)
from pytsonui import setupUi

class serverSwitcher(ts3plugin):
    tag = "server"
    name = 'Server Switcher'
    apiVersion = 22
    requestAutoload = False
    version = '1.0'
    author = 'Bluscream'
    description = 'Show others that you just switched to another tab.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins.'
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Join", "")]
    hotkeys = []
    debug = False
    awaymsg = 'Anderer TS'
    ini = path.join(pytson.getPluginPath(), "scripts", "serverSwitcher", "settings.ini")
    cfg = ConfigParser()

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def parseMeta(self, schid, clid):
        (error, meta) = ts3.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_META_DATA)
        try: meta = re.search('<{0}>(.+?)</{0}>'.format(self.tag), meta).group(0)
        except AttributeError: return False
        return xml.fromstring(meta)

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = {
                "cfgversion": "1",
                "debug": "False",
                "broadcast own changes": "True",
                "broadcast server pw": "False",
                "broadcast new channel": "False",
                "broadcast channel pw": "False",
                "afk status": "switched servers"
            }
            with open(self.ini, 'w') as cfg:
                self.cfg.write(cfg)
        if self.debug: ts3.printMessageToCurrentTab( '{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.'.format(self.timestamp(), self.name, self.author))

    def configure(self, qParentWidget):
        try:
            d = dict()
            for n, v in self.cfg['general'].items():
                if n == "cfgversion": continue
                _type = ValueType.boolean
                if n in ["afk status"]:
                    _type = ValueType.string
                    _var = self.cfg.get('general', n)
                else: _var = self.cfg.getboolean('general', n)
                d[n] = (_type, n.title(), _var, None, None)
            getValues(qParentWidget, self.name, d, self.configDialogClosed)
        except: from traceback import format_exc;ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def configDialogClosed(self, r, vals):
        try:
            if r == QDialog.Accepted:
                for n, v in vals.items():
                    try:
                        if not v == self.cfg.getboolean('general', n):
                            self.cfg.set('general', n, str(v))
                    except: from traceback import format_exc;ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
                with open(self.ini, 'w') as configfile:
                    self.cfg.write(configfile)
        except: from traceback import format_exc;ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT and menuItemID == 0:
            server = self.parseMeta(schid, selectedItemID)
            if not server: return
            port = server.attrib["port"]
            pw = server.attrib["pw"]
            err, tab = ts3.spawnNewServerConnectionHandler(0)
            ts3.startConnection(tab, "", server.attrib["ip"], port if port else 9987, "", [], [], pw if pw else "")
            # ts3.guiConnect(connectTab, serverLabel, serverAddress, serverPassword, nickname, channel, channelPassword, captureProfile, playbackProfile, hotkeyProfile, userIdentity, oneTimeKey, phoneticName)

    def onUpdateClientEvent(self, schid, clientID, invokerID, invokerName, invokerUniqueIdentifier):
        pass

    """
    def onIncomingClientQueryEvent(self, schid, commandText):
            command = commandText.split()
            if command[0] != 'notifyclientupdated': return
            clid = int(command[1].replace('clid=', ''))
            err, ownid = ts3.getClientID(schid)
            if clid != ownid: return
            var = command[2].split("=")
            if var[0] != 'client_input_hardware': return
            if var[1] != '1': return
            self.setStatus(schid, ownid)
    """

    def onClientSelfVariableUpdateEvent(self, schid, flag, oldValue, newValue):
        try:
            if flag == ts3defines.ClientProperties.CLIENT_INPUT_HARDWARE and newValue == "1":
                self.setStatus(schid)
        except: from traceback import format_exc;ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0); pass

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        try:
            if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
                self.setStatus(schid)
        except: from traceback import format_exc;ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0); pass

    def setStatus(self, schid):
        try:
            err, ownid = ts3.getClientID(schid)
            err, schids = ts3.getServerConnectionHandlerList()
            regex = re.compile(r'.*(<{0}>.*</{0}>).*'.format(self.tag), re.IGNORECASE)
            for tab in schids:
                err, meta_data = ts3.getClientSelfVariable(tab, ts3defines.ClientProperties.CLIENT_META_DATA)
                meta_data = regex.sub("", meta_data)
                if tab == schid:
                    ts3.setClientSelfVariableAsInt(tab, ts3defines.ClientPropertiesRare.CLIENT_AWAY, ts3defines.AwayStatus.AWAY_NONE)
                else:
                    err, away_message = ts3.getClientSelfVariable(tab, ts3defines.ClientPropertiesRare.CLIENT_AWAY_MESSAGE)
                    err, away = ts3.getClientSelfVariable(tab, ts3defines.ClientPropertiesRare.CLIENT_AWAY)
                    if away != ts3defines.AwayStatus.AWAY_ZZZ: ts3.setClientSelfVariableAsInt(tab, ts3defines.ClientPropertiesRare.CLIENT_AWAY, ts3defines.AwayStatus.AWAY_ZZZ)
                    if away_message != self.awaymsg: ts3.setClientSelfVariableAsString(tab, ts3defines.ClientPropertiesRare.CLIENT_AWAY_MESSAGE, self.awaymsg)
                    if self.cfg.getboolean('general', 'broadcast own changes'):
                        err, host, port, pw = ts3.getServerConnectInfo(schid)
                        # err, ip = ts3.getConnectionVariableAsString(schid, ownid, ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
                        # err, port = ts3.getConnectionVariableAsString(schid, ownid, ts3defines.ConnectionProperties.CONNECTION_SERVER_PORT)
                        # err, ip = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_IP)
                        # err, port = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_PORT)
                        if host:
                            newmeta = xml.Element(self.tag)
                            err, name = ts3.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
                            if name: newmeta.text = name.strip()
                            newmeta.set("host", host)
                            if port and port != 9987: newmeta.set("port", "{}".format(port))
                            if pw and self.cfg.getboolean('general', 'broadcast server pw'): newmeta.set("pw", pw)
                            meta_data = "{old}{new}".format(old=meta_data,new=xml.tostring(newmeta).decode("utf-8"))
                            # meta_data = "{}<server>{}{}</server>".format(meta_data, ip, ":" + port if port else "")
                ts3.setClientSelfVariableAsString(tab, ts3defines.ClientProperties.CLIENT_META_DATA, meta_data)
                ts3.flushClientSelfUpdates(tab)
        except: from traceback import format_exc;ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0); pass
