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
from xml.sax.saxutils import quoteattr, escape, unescape

class serverSwitcher(ts3plugin):
    tag = "tabs"
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
    ini = path.join(pytson.getPluginPath(), "scripts", "serverSwitcher", "settings.ini")
    cfg = ConfigParser()

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def parseMeta(self, schid, clid):
        (error, meta) = ts3.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_META_DATA)
        # print(re.search('(<{0}.*>.*</{0}>)'.format(self.tag), meta))
        try: meta = re.search('<{0}>(.*)</{0}>'.format(self.tag), meta).group(0)
        except AttributeError: return False
        print('meta_strip: %s'%meta.strip())
        print('xml: %s'%xml.fromstring(meta.strip(), parser = xml.XMLParser(encoding="utf-8")))
        print('xml_sub: %s'%xml.fromstring(meta.strip(), parser = xml.XMLParser(encoding="utf-8")).getchildren())
        print('xml_sub[0]: %s'%xml.fromstring(meta.strip(), parser = xml.XMLParser(encoding="utf-8")).getchildren()[0])
        return xml.fromstring(meta.strip(), parser = xml.XMLParser(encoding="utf-8")).getchildren()[0]

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = {
                "cfgversion": "1",
                "debug": "False",
                "enabled": "True",
                "pw": "False",
                "channel": "False",
                "channelpw": "False",
                "status": "switched servers"
            }
            with open(self.ini, 'w') as cfg:
                self.cfg.write(cfg)
        if self.debug: ts3.printMessageToCurrentTab( '{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.'.format(self.timestamp(), self.name, self.author))

    def configure(self, qParentWidget):
        try:
            d = dict()
            d['debug'] = (ValueType.boolean, "Debug", self.cfg['general']['debug'] == "True", None, None)
            d['enabled'] = (ValueType.boolean, "Broadcast own changes", self.cfg['general']['enabled'] == "True", None, None)
            d['pw'] = (ValueType.boolean, "Broadcast server passwords", self.cfg['general']['pw'] == "True", None, None)
            d['channel'] = (ValueType.boolean, "Broadcast new channel", self.cfg['general']['channel'] == "True", None, None)
            d['channelpw'] = (ValueType.boolean, "Broadcast channel pw", self.cfg['general']['channelpw'] == "True", None, None)
            d['status'] = (ValueType.string, "AFK status text:", self.cfg['general']['status'], None, 1)
            getValues(None, "{} Settings".format(self.name), d, self.configDialogClosed)
        except:
            from traceback import format_exc
            try: ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon::"+self.name, 0)
            except: print("Error in "+self.name+".configure: "+format_exc())

    def configDialogClosed(self, r, vals):
        if r == QDialog.Accepted:
            self.cfg['general'] = {
                "cfgversion": self.cfg.get('general', 'cfgversion'),
                "debug": str(vals['debug']),
                "enabled": str(vals['enabled']),
                "pw": str(vals['pw']),
                "channel": str(vals['channel']),
                "channelpw": str(vals['channelpw']),
                "status": vals['status']
            }
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        try:
            if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT and menuItemID == 0:
                server = self.parseMeta(schid, selectedItemID)
                if server is None: return
                print(server)
                err, tab = ts3.spawnNewServerConnectionHandler(0)
                #rr = ts3.startConnection(tab, identity, ip, port, nickname, defaultChannelArray, defaultChannelPassword, serverPassword)
                err = ts3.startConnection(tab, "", server.attrib["host"], server.attrib["port"] if hasattr(server, "port") else 0, "", [], "", server.attrib["pw"] if hasattr(server, "pw") else "")
                # err, tab = ts3.guiConnect(ts3defines.PluginConnectTab.PLUGIN_CONNECT_TAB_NEW_IF_CURRENT_CONNECTED, server.text or "Server",
                               # '{}:{}'.format(server.attrib["host"], server.attrib["port"]) if hasattr(server, 'port') else server.attrib["host"],
                               # server.attrib["pw"] if hasattr(server, "pw") else "",
                               # "TeamspeakUser","","","","","","","","")
                print(err)
                print(tab)
        except:
            from traceback import format_exc
            try: ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon::"+self.name, 0)
            except: print("Error in "+self.name+".configure: "+format_exc())

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
                    host = "";port = 0; name = ""
                    if self.cfg.getboolean('general', 'enabled'):
                        err, host, port, pw = ts3.getServerConnectInfo(schid)
                        # err, ip = ts3.getConnectionVariableAsString(schid, ownid, ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
                        # err, port = ts3.getConnectionVariableAsString(schid, ownid, ts3defines.ConnectionProperties.CONNECTION_SERVER_PORT)
                        # err, ip = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_IP)
                        # err, port = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_PORT)
                        if host:
                            newmeta = xml.Element(self.tag)
                            c = xml.SubElement(newmeta, "tab")
                            c.set("id", str(schid))
                            err, name = ts3.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
                            if name: c.text = escape(name.strip())
                            c.set("host", escape(host))
                            if port and port != 9987: c.set("port", "{}".format(port))
                            if pw and self.cfg.getboolean('general', 'broadcast server pw'): c.set("pw", pw)
                            meta_data = "{old}{new}".format(old=meta_data,new=xml.tostring(newmeta).decode("utf-8"))
                            # meta_data = "{}<server>{}{}</server>".format(meta_data, ip, ":" + port if port else "")
                    _away_message = self.cfg.get('general', 'status').replace('{host}', host).replace('{port}', str(port)).replace('{name}', name)
                    if away_message != _away_message: ts3.setClientSelfVariableAsString(tab, ts3defines.ClientPropertiesRare.CLIENT_AWAY_MESSAGE, _away_message)
                ts3.setClientSelfVariableAsString(tab, ts3defines.ClientProperties.CLIENT_META_DATA, meta_data)
                ts3.flushClientSelfUpdates(tab)
        except: from traceback import format_exc;ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0); pass
