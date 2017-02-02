from ts3plugin import ts3plugin, PluginHost
import ts3lib as ts3
import ts3defines, datetime, configparser, os.path
from PythonQt.QtGui import QDialog, QInputDialog, QMessageBox, QWidget, QListWidgetItem
from PythonQt.QtCore import Qt
from pytsonui import setupUi
from collections import OrderedDict
from inspect import getmembers

class info(ts3plugin):
    name = "Extended Info"
    apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Shows you more informations.\nBest to use together with a Extended Info Theme.\nClick on \"Settings\" to select what items you want to see :)\n\nHomepage: https://github.com/Bluscream/Extended-Info-Plugin\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = True
    commandKeyword = "info"
    infoTitle = "[b]"+name+":[/b]"
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Set Meta Data", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Set Avatar Flag", "")]
    hotkeys = []
    ini = os.path.join(ts3.getConfigPath(), "plugins", "pyTSon", "scripts", "info", "settings.ini")
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    runs = 0

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
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.cfg.getboolean('general', 'Debug'):
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

    def configDialogClosed(self, r, vals):
        try:
            ts3.printMessageToCurrentTab("vals: "+str(vals))
            if r == QDialog.Accepted:
                for name, val in vals.items():
                    try:
                        if not val == self.cfg.getboolean('general', name):
                            self.cfg.set('general', str(name), str(val))
                    except:
                        from traceback import format_exc
                        ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
                with open(self.ini, 'w') as configfile:
                    self.cfg.write(configfile)
        except:
            from traceback import format_exc
            ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def configure(self, qParentWidget):
        try:
            if not self.dlg:
                self.dlg = SettingsDialog(self)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
        except:
            from traceback import format_exc
            ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def processCommand(self, schid, command):
        tokens = command.split(' ')
        if tokens[0] == "pcmd":
            ts3.sendPluginCommand(schid, tokens[1], ts3defines.PluginTargetMode.PluginCommandTarget_SERVER, []);return True
        elif tokens[0] == "meta":
            if tokens[1] == "get":
                schid = ts3.getCurrentServerConnectionHandlerID()
                error, ownid = ts3.getClientID(schid)
                if error == ts3defines.ERROR_ok:
                    # requestClientVariables(schid, ownid)
                    error, meta = ts3.getClientVariableAsString(schid, ownid, ts3defines.ClientProperties.CLIENT_META_DATA)
                    if error == ts3defines.ERROR_ok:
                        ts3.printMessageToCurrentTab(meta);return True
                    else:
                        ts3.printMessageToCurrentTab("Error: Can't get own meta data.");return True
                else:
                    ts3.printMessageToCurrentTab("Error: Can't get own clientID.");return True
            elif tokens[1] == "set":
                schid = ts3.getCurrentServerConnectionHandlerID()
                error = ts3.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_META_DATA, tokens[2])
                if not error == ts3defines.ERROR_ok:
                    ts3.printMessageToCurrentTab("Error: Unable to set own meta data.");return True
                else: return True
        else:
            ts3.printMessageToCurrentTab("ERROR: Command \""+tokens[0]+"\" not found!");return True
        return False

    def onPluginCommandEvent(self, serverConnectionHandlerID, pluginName, pluginCommand):
            _f = "Plugin message by \""+pluginName+"\": "+pluginCommand
            ts3.logMessage('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())+" "+_f, ts3defines.LogLevel.LogLevel_INFO, self.name, 0)
            if self.cfg.getboolean('general', 'Debug'):
                ts3.printMessageToCurrentTab(_f)
                print(_f)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0:
                schid = ts3.getCurrentServerConnectionHandlerID()
                error, ownid = ts3.getClientID(schid)
                if error == ts3defines.ERROR_ok:
                    error, meta = ts3.getClientVariableAsString(schid, ownid, ts3defines.ClientProperties.CLIENT_META_DATA)
                    if error == ts3defines.ERROR_ok:
                        x = QWidget()
                        meta = QInputDialog.getMultiLineText(x, "Change own Meta Data", "Meta Data:", meta)
                        error = ts3.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_META_DATA, meta)
                        if not error == ts3defines.ERROR_ok:
                            _t = QMessageBox(QMessageBox.Critical, "Error #%s"%error, "Unable to set own meta data!");_t.show()
            elif menuItemID == 1:
                schid = ts3.getCurrentServerConnectionHandlerID()
                error, ownid = ts3.getClientID(schid)
                if error == ts3defines.ERROR_ok:
                    error, flag = ts3.getClientVariableAsString(schid, ownid, ts3defines.ClientPropertiesRare.CLIENT_FLAG_AVATAR)
                    ts3.printMessageToCurrentTab("Your current avatar flag is: %s"%flag)
                    if error == ts3defines.ERROR_ok:
                        x = QWidget()
                        flag = QInputDialog.getText(x, "Change own Avatar Flag", "Avatar File MD5:")
                        error = ts3.setClientSelfVariableAsString(schid, ts3defines.ClientPropertiesRare.CLIENT_FLAG_AVATAR, flag)
                        error2 = ts3.flushClientSelfUpdates(schid)
                        if not error == ts3defines.ERROR_ok and error2 == ts3defines.ERROR_ok:
                            _t = QMessageBox(QMessageBox.Critical, "Error", "Unable to set own avatar flag!");_t.show()

    def infoData(self, schid, id, atype):
        i = []
        schid = ts3.getCurrentServerConnectionHandlerID()
        if atype == 0:
            if self.cfg.getboolean('general', 'Autorequest Server Variables'):
                ts3.requestServerVariables(schid)
            for name in self.cfg['VirtualServerProperties']:
                if name == 'LAST_REQUESTED':
                    if self.cfg.getboolean('VirtualServerProperties', 'LAST_REQUESTED'):
                        i.append('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
                elif name == 'TYPE':
                    if self.cfg.getboolean('VirtualServerProperties', 'TYPE'):
                        i.append('Type: [b]Server[/b]')
                else:
                    try:
                        if self.cfg.getboolean('VirtualServerProperties', name):
                            (success, _tmp) = self.processVariable(schid, 'VirtualServerProperties', name, 'VIRTUALSERVER_', id)
                            if success: i.append(_tmp)
                    except:
                        continue#ts3.logMessage('Could not look up '+name, ts3defines.LogLevel.LogLevel_ERROR, self.name, schid)
            for name in self.cfg['VirtualServerPropertiesRare']:
                try:
                    if self.cfg.getboolean('VirtualServerPropertiesRare', name):
                            (success, _tmp) = self.processVariable(schid, 'VirtualServerPropertiesRare', name, 'VIRTUALSERVER_', id)
                            if success: i.append(_tmp)
                except:
                    continue#ts3.logMessage('Could not look up '+name, ts3defines.LogLevel.LogLevel_ERROR, self.name, schid)
            return i
        elif atype == 1:
            for name in self.cfg['ChannelProperties']:
                if name == 'LAST_REQUESTED':
                    if self.cfg.getboolean('ChannelProperties', 'LAST_REQUESTED'):
                        i.append('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
                elif name == 'TYPE':
                    if self.cfg.getboolean('ChannelProperties', 'TYPE'): i.append('Type: [b]Channel[/b]')
                elif name == 'ID':
                    if self.cfg.getboolean('ChannelProperties', 'ID'):
                        i.append("ID: %s"%id)
                else:
                    try:
                        if self.cfg.getboolean('ChannelProperties', name):
                            (success, _tmp) = self.processVariable(schid, 'ChannelProperties', name, 'CHANNEL_', id)
                            if success: i.append(_tmp)
                    except:
                        continue#ts3.logMessage('Could not look up '+name, ts3defines.LogLevel.LogLevel_ERROR, self.name, schid)
            for name in self.cfg['ChannelPropertiesRare']:
                try:
                    if self.cfg.getboolean('ChannelPropertiesRare', name):
                        (success, _tmp) = self.processVariable(schid, 'ChannelPropertiesRare', name, 'CHANNEL_', id)
                        if success: i.append(_tmp)
                except:
                    continue#ts3.logMessage('Could not look up '+name, ts3defines.LogLevel.LogLevel_ERROR, self.name, schid)
            return i
        elif atype == 2:
            if self.cfg.getboolean('general', 'Autorequest Client Variables'):
                ts3.requestClientVariables(schid, id)
            for name in self.cfg['ClientProperties']:
                if name == 'LAST_REQUESTED':
                    if self.cfg.getboolean('ClientProperties', 'LAST_REQUESTED'):
                        i.append('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
                elif name == 'TYPE':
                    if self.cfg.getboolean('ClientProperties', 'TYPE'):
                        (error, type) = ts3.getClientVariableAsInt(schid, id, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
                        if error == ts3defines.ERROR_ok:
                            if type == ts3defines.ClientType.ClientType_NORMAL:
                                i.append('Type: [b]Client[/b]')
                            elif type == ts3defines.ClientType.ClientType_SERVERQUERY:
                                i.append('Type: [b]ServerQuery[/b]')
                            else: i.append('Type: [b]Unknown ('+str(type)+')[/b]')
                elif name == 'ID':
                    if self.cfg.getboolean('ClientProperties', 'ID'):
                        i.append("ID: %s"%id)
                else:
                    try:
                        if self.cfg.getboolean('ClientProperties', name):
                            (success, _tmp) = self.processVariable(schid, 'ClientProperties', name, 'CLIENT_', id)
                            if success: i.append(_tmp)
                    except:
                        continue;ts3.logMessage('Could not look up '+name, ts3defines.LogLevel.LogLevel_ERROR, self.name, schid)
            for name in self.cfg['ClientPropertiesRare']:
                try:
                    if self.cfg.getboolean('ClientPropertiesRare', name):
                            (success, _tmp) = self.processVariable(schid, 'ClientPropertiesRare', name, 'CLIENT_', id)
                            if success: i.append(_tmp)
                except:
                    continue;ts3.logMessage('Could not look up '+name, ts3defines.LogLevel.LogLevel_ERROR, self.name, schid)
            for name in self.cfg['ConnectionProperties']:
                try:
                    if self.cfg.getboolean('ConnectionProperties', name):
                        (success, _tmp) = self.processVariable(schid, 'ConnectionProperties', name, 'CONNECTION_', id)
                        if success: i.append(_tmp)
                except:
                    continue#ts3.logMessage('Could not look up '+name, ts3defines.LogLevel.LogLevel_ERROR, self.name, schid)
            for name in self.cfg['ConnectionPropertiesRare']:
                try:
                    if self.cfg.getboolean('ConnectionPropertiesRare', name):
                        (success, _tmp) = self.processVariable(schid, 'ConnectionPropertiesRare', name, 'CONNECTION_', id)
                        if success: i.append(_tmp)
                except:
                    continue#ts3.logMessage('Could not look up '+name, ts3defines.LogLevel.LogLevel_ERROR, self.name, schid)
            return i
        else:
            return ["ItemType \""+str(atype)+"\" unknown."]

    def processVariable(self, schid, type, var, start, id):
        try:
            _tmp = eval('ts3defines.%s.%s' % (type, var))
            if "VirtualServerProperties" in type:
                (error, _var) = ts3.getServerVariableAsString(schid, _tmp)
                if _var == "" or error != ts3defines.ERROR_ok: (error, _var) = ts3.getServerVariableAsUInt64(schid, _tmp)
                elif _var is None or _var == 0 or error != ts3defines.ERROR_ok: (error, _var) = ts3.getServerVariableAsInt(schid, _tmp)
            elif "ChannelProperties" in type:
                (error, _var) = ts3.getChannelVariableAsString(schid, id, _tmp)
                if _var == "" or error != ts3defines.ERROR_ok: (error, _var) = ts3.getChannelVariableAsUInt64(schid, id, _tmp)
                elif _var is None or _var == 0 or error != ts3defines.ERROR_ok: (error, _var) = ts3.getChannelVariableAsInt(schid, id, _tmp)
            elif "ClientProperties" in type:
                if id == ts3.getClientID(schid):
                    (error, _var) = ts3.getClientSelfVariableAsString(schid, _tmp)
                    if _var == "" or error != ts3defines.ERROR_ok: (error, _var) = ts3.getClientVariableAsString(schid, id, _tmp)
                    elif _var == "" or error != ts3defines.ERROR_ok: (error, _var) = ts3.getClientVariableAsUInt64(schid, id, _tmp)
                    elif _var is None or _var == 0 or error != ts3defines.ERROR_ok: (error, _var) = ts3.getClientSelfVariableAsInt(schid, id, _tmp)
                    elif _var is None or _var == 0 or error != ts3defines.ERROR_ok: (error, _var) = ts3.getClientVariableAsInt(schid, _tmp)
                else:
                    (error, _var) = ts3.getClientVariableAsString(schid, id, _tmp)
                    if _var == "" or error != ts3defines.ERROR_ok: (error, _var) = ts3.getClientVariableAsUInt64(schid, id, _tmp)
                    elif _var is None or _var == 0 or error != ts3defines.ERROR_ok: (error, _var) = ts3.getClientVariableAsInt(schid, _tmp)
            elif "ConnectionProperties" in type:
                (error, _var) = ts3.getConnectionVariableAsString(schid, id, _tmp)
                if _var == "" or error != ts3defines.ERROR_ok: (error, _var) = ts3.getConnectionVariableAsUInt64(schid, id, _tmp)
                elif _var is None or _var == 0 or error != ts3defines.ERROR_ok: (error, _var) = ts3.getConnectionVariableAsInt(schid, id, _tmp)
            _var = str(_var)
            if error != ts3defines.ERROR_ok or _var == "": return False, ""
            return True, var.replace(start, '').replace('_', ' ').title() + ": " + _var
        except: from traceback import format_exc;ts3.logMessage("Could not resolve variable ts3defines.%s.%s: %s" % (type, var, format_exc()), ts3defines.LogLevel.LogLevel_INFO, self.name, 0);return False, ""

class SettingsDialog(QDialog):
    def __init__(self,info, parent=None):
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "info", "settings.ui"))
        self.setWindowTitle("Extended Info Settings")
        ts3.printMessageToCurrentTab(str(info.cfg.getboolean('general', 'Debug')))
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
    def on_btn_apply_clicked(self):
        ts3.printMessageToCurrentTab("on_btn_apply_clicked")
        info.cfg.set('general', 'Debug', str(self.chk_debug.isChecked()))
        info.cfg.set('general', 'Colored', str(self.chk_colored.isChecked()))
        info.cfg.set('general', 'Autorequest Server Variables', str(self.chk_arsv.isChecked()))
        info.cfg.set('general', 'Autorequest Client Variables', str(self.chk_arcv.isChecked()))
        # for
        with open(info.ini, 'w') as configfile:
            info.cfg.write(configfile)
