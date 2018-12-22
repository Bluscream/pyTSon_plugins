import os.path, inspect, re, traceback, json, ts3lib, requests
from ts3plugin import ts3plugin, PluginHost
from ts3defines import *
from PythonQt.QtGui import QDialog, QInputDialog, QMessageBox, QWidget, QListWidgetItem, QTableWidgetItem
from PythonQt.QtCore import Qt, QUrl
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
from pytsonui import setupUi
from collections import OrderedDict
from inspect import getmembers
from configparser import ConfigParser
from urllib.parse import quote as urlencode
from bluscream import timestamp, clientURL, channelURL, serverURL, Time, getItems, getItemType
from datetime import timedelta, date, datetime

class info(ts3plugin):
    name = "Extended Info"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Shows you more informations.\nBest to use together with a Extended Info Theme.\nClick on \"Settings\" to select what items you want to see :)\n\nHomepage: https://github.com/Bluscream/Extended-Info-Plugin\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = True
    commandKeyword = "info"
    infoTitle = "[b]Extendend Info[/b]"
    menuItems = [
        (PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Set Meta Data", "scripts/%s/meta_data.svg"%__name__),
        (PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "Set Avatar Flag", "scripts/%s/avatar_flag.svg"%__name__),
        (PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Extended Info", "scripts/%s/info.svg"%__name__),
        (PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Extended Info", "scripts/%s/info.svg"%__name__),
        (PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Extended Info", "scripts/%s/info.svg"%__name__)
    ]
    hotkeys = []
    ini = os.path.join(ts3lib.getConfigPath(), "plugins", "pyTSon", "scripts", "info", "settings.ini")
    cfg = ConfigParser()
    cfg.optionxform = str
    runs = 0
    requested = []
    requestedCLIDS = []

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
            for name, value in getmembers(VirtualServerProperties):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER'):
                    self.cfg.set("VirtualServerProperties", name, "False")
            for name, value in getmembers(VirtualServerPropertiesRare):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER_RARE'):
                    self.cfg.set("VirtualServerPropertiesRare", name, "False")
            self.cfg.set("ChannelProperties", "LAST_REQUESTED", "True");self.cfg.set("ChannelProperties", "TYPE", "True");self.cfg.set("ChannelProperties", "ID", "True")
            for name, value in getmembers(ChannelProperties):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER'):
                    self.cfg.set("ChannelProperties", name, "False")
            for name, value in getmembers(ChannelPropertiesRare):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER_RARE'):
                    self.cfg.set("ChannelPropertiesRare", name, "False")
            self.cfg.set("ClientProperties", "LAST_REQUESTED", "True");self.cfg.set("ClientProperties", "TYPE", "True");self.cfg.set("ClientProperties", "ID", "True");self.cfg.set("ClientProperties", "DISPLAYNAME", "True")
            for name, value in getmembers(ClientProperties):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER'):
                    self.cfg.set("ClientProperties", name, "False")
            for name, value in getmembers(ClientPropertiesRare):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER_RARE'):
                    self.cfg.set("ClientPropertiesRare", name, "False")
            for name, value in getmembers(ConnectionProperties):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER'):
                    self.cfg.set("ConnectionProperties", name, "False")
            for name, value in getmembers(ConnectionPropertiesRare):
                if not name.startswith('__') and not '_DUMMY_' in name and not name.endswith('_ENDMARKER_RARE'):
                    self.cfg.set('ConnectionPropertiesRare', name, 'False')
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        if self.cfg.getboolean('general', 'Debug'):
            ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def configDialogClosed(self, r, vals):
        try:
            if r == QDialog.Accepted:
                for name, val in vals.items():
                    try:
                        if not val == self.cfg.getboolean('general', name):
                            self.cfg.set('general', str(name), str(val))
                    except:
                        if self.cfg.getboolean('general', 'Debug'): from traceback import format_exc;ts3lib.logMessage(format_exc(), LogLevel.LogLevel_ERROR, "PyTSon", 0)
                with open(self.ini, 'w') as configfile:
                    self.cfg.write(configfile)
        except:
            if self.cfg.getboolean('general', 'Debug'): from traceback import format_exc;ts3lib.logMessage(format_exc(), LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def configure(self, qParentWidget):
        try:
            if not self.dlg:
                self.dlg = SettingsDialog(self)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
        except:
            if self.cfg.getboolean('general', 'Debug'): from traceback import format_exc;ts3lib.logMessage(format_exc(), LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def processCommand(self, schid, cmd):
        cmd = cmd.split(' ', 1)
        command = cmd[0].lower()
        id = int(cmd[1])
        if command == "client":
            (err, cid) = ts3lib.getChannelOfClient(schid, id)
            ts3lib.printMessageToCurrentTab("<{}> Client {} in channel {}".format(Time(), clientURL(schid, id), channelURL(schid, cid)))
            return True
        elif command == "channel":
            (err, clids) = ts3lib.getChannelClientList(schid, id)
            channel_clients = []
            for clid in clids: channel_clients.append(clientURL(schid, clid))
            ts3lib.printMessageToCurrentTab("<{}> Channel {} with [b]{}[/b] clients: {}".format(Time(), channelURL(schid, id), len(clids), ','.join(channel_clients)))
            return True
        elif command == "server":
            ts3lib.printMessageToCurrentTab("<{}> Server {}".format(Time(), serverURL(schid)))
            return True
        else:
            ts3lib.printMessageToCurrentTab(schid, "Syntax: /py info client/channel/server <id>")
            return False


    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            if not self.dlg:
                self.dlg = VariablesDialog(self, schid, atype, selectedItemID)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
        else:
            if atype == PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
                err, ownid = ts3lib.getClientID(schid)
                if err != ERROR_ok: return
                if menuItemID == 1:
                    error, meta = ts3lib.getClientVariableAsString(schid, ownid, ClientProperties.CLIENT_META_DATA)
                    if error == ERROR_ok:
                        x = QWidget()
                        _meta = QInputDialog.getMultiLineText(x, "Change own Meta Data", "Meta Data:", meta)
                        if _meta == meta: return
                        error = ts3lib.setClientSelfVariableAsString(schid, ClientProperties.CLIENT_META_DATA, _meta)
                        if not error == ERROR_ok:
                            _t = QMessageBox(QMessageBox.Critical, "Error #%s"%error, "Unable to set own meta data!");_t.show()
                elif menuItemID == 2:
                    err, flag = ts3lib.getClientVariableAsString(schid, ownid, ClientPropertiesRare.CLIENT_FLAG_AVATAR)
                    ts3lib.printMessageToCurrentTab("Your current avatar flag is: %s"%flag)
                    x = QWidget()
                    _flag = QInputDialog.getText(x, "Change own Avatar Flag", "Avatar File MD5:")
                    if _flag == "x" or _flag.strip() == flag.strip(): return
                    error = ts3lib.setClientSelfVariableAsString(schid, ClientPropertiesRare.CLIENT_FLAG_AVATAR, _flag)
                    error2 = ts3lib.flushClientSelfUpdates(schid)
                    if not error == ERROR_ok or not error2 == ERROR_ok:
                        _t = QMessageBox(QMessageBox.Critical, "Error", "Unable to set own avatar flag!");_t.show()

    def getInfo(self, schid, selectedItemID, lists):
        i = []
        for lst in lists:
            for name, var in getItems(lst):
                (name, var) = self.preProcessVar(schid, selectedItemID, name, var, lst)
                if var is None: continue
                if lst in [VirtualServerProperties, VirtualServerPropertiesRare]:
                    (err, var) = ts3lib.getServerVariable(schid, var)
                elif lst in [ChannelProperties, ChannelPropertiesRare]:
                    (err, var) = ts3lib.getChannelVariable(schid, selectedItemID, var)
                elif lst in [ConnectionProperties, ConnectionPropertiesRare]:
                    (err, var) = ts3lib.getConnectionVariable(schid, selectedItemID, var)
                else:
                    (err, var) = ts3lib.getClientVariable(schid, selectedItemID, var)
                if err != ERROR_ok or var == "" or var == 0: continue
                if isinstance(var, map): var = ", ".join(map(str, var))
                if name in ["VIRTUALSERVER_IP","CONNECTION_CLIENT_IP"]: i.extend(self.ipInfo(var))
                (name, var) = self.postProcessVar(schid, selectedItemID, name, var, lst)
                i.append('{0}: {1}'.format(name, var))
        return i

    def preProcessVar(self, schid, id, name, var, lst):
        return name, var
        if name == "CLIENT_META_DATA":
            (err, ownID) = ts3lib.getClientID(schid)
            if id == ownID: return name, None
        elif name == "CHANNEL_PASSWORD": return name, None
        return name, var

    def postProcessVar(self, schid, id, name, val, lst): # TODO Check Why version is "3.1.3 [Build"
        if name in [
            "VIRTUALSERVER_CREATED",
            "CLIENT_LAST_VAR_REQUEST",
            "CLIENT_CREATED",
            "CLIENT_LASTCONNECTED"
        ]:
            timeobj = datetime.fromtimestamp(val).strftime('%Y-%m-%d %H:%M:%S')
            val = "{} ({})".format(timeobj, val)
        elif name in [
            "VIRTUALSERVER_UPTIME",
            "VIRTUALSERVER_COMPLAIN_AUTOBAN_TIME",
            "VIRTUALSERVER_COMPLAIN_REMOVE_TIME",
            "CHANNEL_DELETE_DELAY",
            "CLIENT_IDLE_TIME",
            "CONNECTION_IDLE_TIME"
        ]:
            val = '{0} ({1})'.format(timedelta(seconds=val), val)
        elif name in [
            "CONNECTION_CONNECTED_TIME"
        ]:
            val = '{0} ({1})'.format(timedelta(milliseconds=val), val)
        elif name == "TYPE": (t,val) = getItemType(lst)
        elif name == "ID": return name, id
        elif name == "DISPLAYNAME": (err, val) = ts3lib.getClientDisplayName(schid, id)
        if lst in [VirtualServerProperties, VirtualServerPropertiesRare]:
            name = name.replace("VIRTUALSERVER_", "")
        elif lst in [ChannelProperties, ChannelPropertiesRare]:
            name = name.replace("CHANNEL_", "")
        elif lst in [ConnectionProperties, ConnectionPropertiesRare]:
            name = name.replace("CONNECTION_", "")
        elif lst in [ClientProperties, ClientPropertiesRare]:
            name = name.replace("CLIENT_", "")
        return name.replace("_", " ").title(), val

    def onServerUpdatedEvent(self, schid):
        return # TODO: Check
        if schid in self.requested: return
        self.requested.append(schid)
        ts3lib.requestInfoUpdate(schid, PluginItemType.PLUGIN_SERVER, schid)

    def onConnectionInfoEvent(self, schid, clid):
        if clid in self.requestedCLIDS: return
        self.requestedCLIDS.append(clid)
        ts3lib.requestInfoUpdate(schid, PluginItemType.PLUGIN_CLIENT, schid)

    def onUpdateClientEvent(self, schid, clid, invokerID, invokerName, invokerUniqueIdentifier):
        if clid in self.requestedCLIDS: return
        self.requestedCLIDS.append(clid)
        ts3lib.requestInfoUpdate(schid, PluginItemType.PLUGIN_CLIENT, schid)

    def ipInfo(self, ip):
        url = 'http://ip-api.com/json/{0}'.format(ip)
        print('Requesting {0}'.format(url))
        i = []
        r = requests.get(url)
        if r.status_code != requests.codes.ok: return i
        for k,v in r.json().items():
            if v is None or v == "" or k in ["status", "query", "message"]: continue
            i.append('{0}: {1}'.format(k.title(), v))
        return i
        # self.nwmc = QNetworkAccessManager()
        # self.nwmc.connect("finished(QNetworkReply*)", self.ipReply)
        # self.nwmc.get(QNetworkRequest(QUrl(url)))

    def ipReply(self, reply):
        i = []
        r = json.loads(reply.readAll().data().decode('utf-8'))
        for n, v in r:
            i.append('{0}: {1}'.format(n.title(), v))
        return i if len(i) > 0 else None

    def getServerInfo(self, schid):
        i = []
        (err, host, port, password) = ts3lib.getServerConnectInfo(schid)
        i.append('Host: {0}'.format(host))
        if port: i.append('Port: {0}'.format(port))
        if password != "": i.append('Password: {0}'.format(password))
        i.extend(self.getInfo(schid, None, [VirtualServerProperties, VirtualServerPropertiesRare]))
        return i if len(i) > 0 else None

    def getChannelInfo(self, schid, cid):
        i = []
        (err, path, password) = ts3lib.getChannelConnectInfo(schid, cid)
        (err, name) = ts3lib.getChannelVariable(schid, cid, ChannelProperties.CHANNEL_NAME)
        if path != name: i.append('Path: {0}'.format(path))
        if password != "": i.append('Password: {0}'.format(password))
        i.extend(self.getInfo(schid, cid, [ChannelProperties, ChannelPropertiesRare]))
        return i if len(i) > 0 else None

    def getClientInfo(self, schid, clid):
        i = []
        i.extend(self.getInfo(schid, clid, [ClientProperties, ClientPropertiesRare, ConnectionProperties, ConnectionPropertiesRare]))
        return i if len(i) > 0 else None

    def infoData(self, schid, id, atype):
        if not self.cfg.getboolean('general', 'InfoData'): return
        return self.getInfoData(schid, id, atype)

    def getInfoData(self, schid, id, atype):
        # print("schid",schid,"id",id,"atype",atype)
        if atype == PluginItemType.PLUGIN_SERVER:
            if not schid in self.requested:
                ts3lib.requestServerVariables(schid)
            return self.getServerInfo(schid)
        elif atype == PluginItemType.PLUGIN_CHANNEL:
            return self.getChannelInfo(schid, id)
        elif atype == PluginItemType.PLUGIN_CLIENT:
            if not id in self.requestedCLIDS:
                ts3lib.requestConnectionInfo(schid, id)
            return self.getClientInfo(schid, id)
        return None

class VariablesDialog(QDialog):
    def __init__(self, info, schid, atype, selectedItemID, parent=None):
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "info", "variables.ui"))
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.info = info
        self.schid = schid
        self.atype = atype
        self.selectedItemID = selectedItemID
        self.setupTable()

    def setupTable(self):
        tbl = self.tbl_variables
        tbl.clearContents()
        tbl.setRowCount(0)
        for i in self.info.getInfoData(self.schid, self.selectedItemID, self.atype):
            k = i.split(': ')[0]
            v = i.split(': ')[1]
            pos = tbl.rowCount
            tbl.insertRow(pos)
            tbl.setItem(pos, 0, QTableWidgetItem(k))
            tbl.setItem(pos, 1, QTableWidgetItem(v))
        name = info.name
        if self.atype == PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            err, name = ts3lib.getServerVariable(self.schid, VirtualServerProperties.VIRTUALSERVER_NAME)
        elif self.atype == PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL:
            err, name = ts3lib.getChannelVariable(self.schid, self.selectedItemID, ChannelProperties.CHANNEL_NAME)
        elif self.atype == PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            err, name = ts3lib.getClientVariable(self.schid, self.selectedItemID, ClientProperties.CLIENT_NICKNAME)
        tbl.sortItems(0)
        self.setWindowTitle("{}'s Variables".format(name))

    def on_btn_close_clicked(self): self.close()
    def on_btn_reload_clicked(self): self.setupTable()

class SettingsDialog(QDialog):
    def __init__(self, info, parent=None):
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "info", "settings.ui"))
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Extended Info Settings")
        self.chk_debug.setChecked(info.cfg.getboolean('general', 'Debug'))
        self.chk_colored.setChecked(info.cfg.getboolean('general', 'Colored'))
        self.chk_arsv.setChecked(info.cfg.getboolean('general', 'Autorequest Server Variables'))
        self.chk_arcv.setChecked(info.cfg.getboolean('general', 'Autorequest Client Variables'))
        for name, value in info.cfg['VirtualServerProperties'].items():
            _item = QListWidgetItem(self.lst_server)
            _item.setToolTip(name)
            _item.setStatusTip('VirtualServerProperties')
            if value.lower() == "true": _item.setCheckState(Qt.Checked)
            else: _item.setCheckState(Qt.Unchecked)
            _item.setText(name.replace('VIRTUALSERVER_', '').replace('_', ' ').title())
        for name, value in info.cfg['VirtualServerPropertiesRare'].items():
            _item = QListWidgetItem(self.lst_server)
            _item.setToolTip(name)
            _item.setStatusTip('VirtualServerPropertiesRare')
            if value.lower() == "true": _item.setCheckState(Qt.Checked)
            else: _item.setCheckState(Qt.Unchecked)
            _item.setText(name.replace('VIRTUALSERVER_', '').replace('_', ' ').title())
        for name, value in info.cfg['ChannelProperties'].items():
            _item = QListWidgetItem(self.lst_channel)
            _item.setToolTip(name)
            _item.setStatusTip('ChannelProperties')
            if value.lower() == "true": _item.setCheckState(Qt.Checked)
            else: _item.setCheckState(Qt.Unchecked)
            _item.setText(name.replace('CHANNEL_', '').replace('_', ' ').title())
        for name, value in info.cfg['ChannelPropertiesRare'].items():
            _item = QListWidgetItem(self.lst_channel)
            _item.setToolTip(name)
            _item.setStatusTip('ChannelPropertiesRare')
            if value.lower() == "true": _item.setCheckState(Qt.Checked)
            else: _item.setCheckState(Qt.Unchecked)
            _item.setText(name.replace('CHANNEL_', '').replace('_', ' ').title())
        for name, value in info.cfg['ClientProperties'].items():
            _item = QListWidgetItem(self.lst_client)
            _item.setToolTip(name)
            _item.setStatusTip('ClientProperties')
            if value.lower() == "true": _item.setCheckState(Qt.Checked)
            else: _item.setCheckState(Qt.Unchecked)
            _item.setText(name.replace('CLIENT_', '').replace('_', ' ').title())
        for name, value in info.cfg['ClientPropertiesRare'].items():
            _item = QListWidgetItem(self.lst_client)
            _item.setToolTip(name)
            _item.setStatusTip('ClientPropertiesRare')
            if value.lower() == "true": _item.setCheckState(Qt.Checked)
            else: _item.setCheckState(Qt.Unchecked)
            _item.setText(name.replace('CLIENT_', '').replace('_', ' ').title())
        for name, value in info.cfg['ConnectionProperties'].items():
            _item = QListWidgetItem(self.lst_client)
            _item.setToolTip(name)
            _item.setStatusTip('ConnectionProperties')
            if value.lower() == "true": _item.setCheckState(Qt.Checked)
            else: _item.setCheckState(Qt.Unchecked)
            _item.setText(name.replace('CONNECTION_', '').replace('_', ' ').title())
        for name, value in info.cfg['ConnectionPropertiesRare'].items():
            _item = QListWidgetItem(self.lst_client)
            _item.setToolTip(name)
            _item.setStatusTip('ConnectionPropertiesRare')
            if value.lower() == "true": _item.setCheckState(Qt.Checked)
            else: _item.setCheckState(Qt.Unchecked)
            _item.setText(name.replace('CONNECTION_', '').replace('_', ' ').title())
        self.info = info

    def iterAllItems(self, parent):
        for i in range(parent.count()):
            yield parent.item(i)

    def on_btn_apply_clicked(self):
        if self.info.cfg.getboolean('general', 'Debug'): ts3lib.printMessageToCurrentTab("on_btn_apply_clicked")
        self.info.cfg.set('general', 'Debug', str(self.chk_debug.isChecked()))
        self.info.cfg.set('general', 'InfoData', str(self.chk_infodata.isChecked()))
        self.info.cfg.set('general', 'Colored', str(self.chk_colored.isChecked()))
        self.info.cfg.set('general', 'Autorequest Server Variables', str(self.chk_arsv.isChecked()))
        self.info.cfg.set('general', 'Autorequest Client Variables', str(self.chk_arcv.isChecked()))
        for item in self.iterAllItems(self.lst_server):
            if self.info.cfg.has_option('VirtualServerProperties', item.tooltip()):
                self.info.cfg.set('VirtualServerProperties', item.toolTip(), str(item.checkState() == Qt.Checked))
            elif self.info.cfg.has_option('VirtualServerPropertiesRare', item.tooltip()):
                self.info.cfg.set('VirtualServerPropertiesRare', item.toolTip(), str(item.checkState() == Qt.Checked))
        for item in self.iterAllItems(self.lst_channel):
            if self.info.cfg.has_option('ChannelProperties', item.tooltip()):
          	    self.info.cfg.set('ChannelProperties', item.toolTip(), str(item.checkState() == Qt.Checked))
            elif self.info.cfg.has_option('ChannelPropertiesRare', item.tooltip()):
          	    self.info.cfg.set('ChannelPropertiesRare', item.toolTip(), str(item.checkState() == Qt.Checked))
        for item in self.iterAllItems(self.lst_client):
            if self.info.cfg.has_option('ClientProperties', item.tooltip()):
         	    self.info.cfg.set('ClientProperties', item.toolTip(), str(item.checkState() == Qt.Checked))
            elif self.info.cfg.has_option('ClientPropertiesRare', item.tooltip()):
         	    self.info.cfg.set('ClientPropertiesRare', item.toolTip(), str(item.checkState() == Qt.Checked))
            elif self.info.cfg.has_option('ConnectionProperties', item.tooltip()):
       	  	    self.info.cfg.set('ConnectionProperties', item.toolTip(), str(item.checkState() == Qt.Checked))
            elif self.info.cfg.has_option('ConnectionPropertiesRare', item.tooltip()):
        	    self.info.cfg.set('ConnectionPropertiesRare', item.toolTip(), str(item.checkState() == Qt.Checked))
        with open(self.info.ini, 'w') as configfile:
            self.info.cfg.write(configfile)

###########################################################################
#
#  update_items() -> None
#      |
#      V
#  get_items() -> namedtuple('Item', ('item', 'irgendwas', 'name', ''))
#      |
#      V
#  save_to_cfg() -> None
#
#  --> c==3
#
############################################################################
