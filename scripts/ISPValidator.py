from ts3plugin import ts3plugin, PluginHost
from pytsonui import setupUi, getValues, ValueType
from PythonQt.QtGui import *
from PythonQt.QtCore import QUrl, Qt
from PythonQt.QtNetwork import *
from traceback import format_exc
from urllib.parse import quote as urlencode
from os import path
from configparser import ConfigParser
import ts3, ts3defines

class ISPValidator(ts3plugin):
    name = "ISP Validator"
    apiVersion = 21
    requestAutoload = False
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
    schid = 0
    dlg = None
    isps = path.join(ts3.getPluginPath(), "pyTSon", "scripts", "ISPValidator", "isps.txt")

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = { "debug": "False", "whitelist": "True", "isps": self.isps }
            self.cfg['main'] = { "kickonly": "False", "bantime": "60", "reason": "{isp} is not a valid home Internet Service Provider!" }
            self.cfg['failover'] = { "enabled": "False", "kickonly": "False", "bantime": "60", "reason": "{isp} is not a valid home Internet Service Provider!" }
            self.cfg['api'] = { "main": "http://ip-api.com/line/{ip}?fields=isp", "fallback": "http://ipinfo.io/{ip}/org" }
            self.cfg['events'] = { "own client connected": "True", "client connected": "True", "client ip changed": "False" }
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        with open(self.cfg['general']['isps']) as f:
            self.isps = f.readlines()
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)

    def configure(self, qParentWidget):
        try:
            if not self.dlg:
                self.dlg = SettingsDialog(self)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
        except:
            ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        if not self.cfg.getboolean("events", "own client connected"): return
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            (error, ids) = ts3.getClientList(serverConnectionHandlerID)
            if error == ts3defines.ERROR_ok:
                for _in in ids:
                    (error, _type) = ts3.getClientVariableAsInt(serverConnectionHandlerID, clientID, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
                    if error == ts3defines.ERROR_ok and _type == 0:
                        self.requested = clientID;self.schid = serverConnectionHandlerID
                        ts3.requestConnectionInfo(serverConnectionHandlerID, clientID)
                    elif error == ts3defines.ERROR_ok and _type == 1: return
                    else: ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the client type of '%s'" % self.clientURL(serverConnectionHandlerID, clientID));return

    def onUpdateClientEvent(self, serverConnectionHandlerID, clientID, invokerID, invokerName, invokerUniqueIdentifier):
        if not self.cfg.getboolean("events", "client ip changed"): return
        if not invokerID == 0: return
        (error, _type) = ts3.getClientVariableAsInt(serverConnectionHandlerID, clientID, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
        if error == ts3defines.ERROR_ok and _type == 0:
            self.requested = clientID;self.schid = serverConnectionHandlerID
            ts3.requestConnectionInfo(serverConnectionHandlerID, clientID)
        elif error == ts3defines.ERROR_ok and _type == 1: return
        else: ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the client type of '%s'" % self.clientURL(serverConnectionHandlerID, clientID));return

    def onClientMoveEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.cfg.getboolean("events", "client connected"): return
        if oldChannelID == 0:
            (error, _type) = ts3.getClientVariableAsInt(serverConnectionHandlerID, clientID, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
            if error == ts3defines.ERROR_ok and _type == 0:
                self.requested = clientID;self.schid = serverConnectionHandlerID
                ts3.requestConnectionInfo(serverConnectionHandlerID, clientID)
            elif error == ts3defines.ERROR_ok and _type == 1: return
            else: ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the client type of '%s'" % self.clientURL(serverConnectionHandlerID, clientID));return

    def onConnectionInfoEvent(self, serverConnectionHandlerID, clientID):
        try:
            if not self.requested == clientID: return
            (error, ip) = ts3.getConnectionVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
            if error == ts3defines.ERROR_ok:
                self.ip = ip
                self.nwm = QNetworkAccessManager()
                self.nwm.connect("finished(QNetworkReply*)", self.onMainReply)
                self.nwm.get(QNetworkRequest(QUrl(self.cfg['api']['main'].replace("{ip}",ip))))
                if self.cfg.getboolean("general", "debug"): ts3.printMessageToCurrentTab(self.cfg['api']['main'].replace("{ip}",ip))
            else:
                (e, msg) = ts3.getErrorMessage(error)
                ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the IP for '%s' (Reason: %s)" % (self.clientURL(serverConnectionHandlerID, clientID),msg))
        except:
            ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the IP for '%s' (Reason: %s)" % (self.clientURL(serverConnectionHandlerID, clientID),format_exc()))
    def onMainReply(self, reply):
        if reply.error() == QNetworkReply.NoError:
            try:
                isp = reply.readAll().data().decode('utf-8')
                if isp.startswith('AS'): isp = isp.split(" ", 1)[1]
                if not isp or isp == "" or isp == "undefined":
                    ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s) Falling back to %s" % (self.clientURL(self.schid, self.requested),format_exc(),self.cfg['api']['fallback'].replace("{ip}",self.ip)))
                    if self.cfg.getboolean("general", "debug"): ts3.printMessageToCurrentTab(self.cfg['api']['fallback'].replace("{ip}",self.ip))
                    self.nwb = QNetworkAccessManager();self.nwb.connect("finished(QNetworkReply*)", self.onFallbackReply)
                    self.nwb.get(QNetworkRequest(QUrl(self.cfg['api']['fallback'].replace("{ip}",self.ip))));return
                if self.cfg.getboolean("general", "debug"): ts3.printMessageToCurrentTab("%s's ISP: %s"%(self.clientURL(self.schid, self.requested),isp))
                _match = False
                for _isp in self.isps:
                    if isp == _isp: _match = True
                if self.cfg.getboolean('general', 'whitelist') and not _match:
                    if self.cfg.getboolean('main', 'kickonly'):
                        ts3.requestClientKickFromServer(self.schid, self.requested, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                    else: ts3.banclient(self.schid, self.requested, 60, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                elif not self.cfg.getboolean('general', 'whitelist') and _match:
                    if self.cfg.getboolean('main', 'kickonly'):
                        ts3.requestClientKickFromServer(self.schid, self.requested, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                    else: ts3.banclient(self.schid, self.requested, 60, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
            except:
                try:
                    ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s) Falling back to %s" % (self.clientURL(self.schid, self.requested),format_exc(),self.cfg['api']['fallback'].replace("{ip}",self.ip)))
                    if self.cfg.getboolean("general", "debug"): ts3.printMessageToCurrentTab(self.cfg['api']['fallback'].replace("{ip}",self.ip))
                    self.nwb = QNetworkAccessManager();self.nwb.connect("finished(QNetworkReply*)", self.onFallbackReply)
                    self.nwb.get(QNetworkRequest(QUrl(self.cfg['api']['fallback'].replace("{ip}",self.ip))))
                except:
                    ts3.printMessageToCurrentTab(format_exc())
        else:
            ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s) Falling back to %s" % (self.clientURL(self.schid, self.requested),reply.errorString(),self.cfg['api']['fallback'].replace("{ip}",self.ip)))
            if self.cfg.getboolean("general", "debug"): ts3.printMessageToCurrentTab(self.cfg['api']['fallback'].replace("{ip}",self.ip))
            self.nwb = QNetworkAccessManager();self.nwb.connect("finished(QNetworkReply*)", self.onFallbackReply)
            self.nwb.get(QNetworkRequest(QUrl(self.cfg['api']['fallback'].replace("{ip}",self.ip))))
        reply.deleteLater()

    def onFallbackReply(self, reply):
        if reply.error() == QNetworkReply.NoError:
            try:
                isp = reply.readAll().data().decode('utf-8')
                if isp.startswith('AS'): isp = isp.split(" ", 1)[1]
                if not isp or isp == "" or isp == "undefined":
                    ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s)" % (self.clientURL(self.schid, self.requested),format_exc()))
                    if self.cfg.getboolean("failover", "enabled"):
                        if self.cfg.getboolean('failover', 'kickonly'):
                            ts3.requestClientKickFromServer(self.schid, self.requested, self.cfg['failover']['reason'].replace('{isp}', isp));
                        else: ts3.banclient(self.schid, self.requested, int(self.cfg['failover']['bantime']), self.cfg['failover']['reason'].replace('{isp}', isp))
                        self.requested = 0;reply.deleteLater();return
                if self.cfg.getboolean("general", "debug"): ts3.printMessageToCurrentTab("%s's ISP: %s"%(self.clientURL(self.schid, self.requested),isp))
                _match = False
                for _isp in self.isps:
                    if isp == _isp: _match = True
                if self.cfg.getboolean('general', 'whitelist') and not _match:
                    if self.cfg.getboolean('main', 'kickonly'):
                        ts3.requestClientKickFromServer(self.schid, self.requested, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                    else: ts3.banclient(self.schid, self.requested, 60, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                elif not self.cfg.getboolean('general', 'whitelist') and _match:
                    if self.cfg.getboolean('main', 'kickonly'):
                        ts3.requestClientKickFromServer(self.schid, self.requested, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                    else: ts3.banclient(self.schid, self.requested, 60, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
            except:
                ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s)" % (self.clientURL(self.schid, self.requested),format_exc()))
                if self.cfg.getboolean("failover", "enabled"):
                    if self.cfg.getboolean('failover', 'kickonly'):
                        ts3.requestClientKickFromServer(self.schid, self.requested, self.cfg['failover']['reason'].replace('{isp}', isp));
                    else: ts3.banclient(self.schid, self.requested, int(self.cfg['failover']['bantime']), self.cfg['failover']['reason'].replace('{isp}', isp))
        else:
            ts3.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s)" % (self.clientURL(self.schid, self.requested),reply.errorString()))
            if self.cfg.getboolean("failover", "enabled"):
                if self.cfg.getboolean('failover', 'kickonly'):
                    ts3.requestClientKickFromServer(self.schid, self.requested, self.cfg['failover']['reason'].replace('{isp}', isp));
                else: ts3.banclient(self.schid, self.requested, int(self.cfg['failover']['bantime']), self.cfg['failover']['reason'].replace('{isp}', isp))
        self.requested = 0
        reply.deleteLater()

    def clientURL(self, schid, clid, uid=None, nickname=None):
        if not nickname:
            (error, uid) = ts3.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            (error, nickname) = ts3.getClientDisplayName(schid, clid)
        encodednick = urlencode(nickname)
        return "[url=client://%s/%s~%s]%s[/url]" % (clid, uid, encodednick, nickname)

class SettingsDialog(QDialog):
    def __init__(self,this, parent=None):
        try:
            self.this = this
            super(QDialog, self).__init__(parent)
            setupUi(self, path.join(ts3.getPluginPath(), "pyTSon", "scripts", "ISPValidator", "settings.ui"))
            self.setWindowTitle("%s Settings" % this.name )
            self.chk_debug.setChecked(this.cfg.getboolean("general", "debug"))
            if this.cfg.getboolean("general", "whitelist"): self.chk_whitelist.setChecked(True)
            else: self.chk_blacklist.setChecked(True)
            if this.cfg.getboolean("main", "kickonly"): self.chk_kick.setChecked(True)
            else: self.chk_ban.setChecked(True)
            if this.cfg.getboolean("failover", "kickonly"): self.chk_kick_2.setChecked(True)
            else: self.chk_ban_2.setChecked(True)
            self.bantime.setValue(int(this.cfg["main"]["bantime"]))
            self.bantime_2.setValue(int(this.cfg["failover"]["bantime"]))
            self.reason.setText(this.cfg["main"]["reason"])
            self.reason_2.setText(this.cfg["failover"]["reason"])
            self.api_main.setText(this.cfg["api"]["main"])
            self.api_fallback.setText(this.cfg["api"]["fallback"])
            if this.cfg.getboolean("failover", "enabled"): self.chk_failover.setChecked(True)
            for event, value in this.cfg["events"].items():
                _item = QListWidgetItem(self.lst_events)
                _item.setToolTip(value)
                _item.setText(event.title())
                if value == "True": _item.setCheckState(Qt.Checked)
                else: _item.setCheckState(Qt.Unchecked)
        except:
            ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def on_chk_kick_toggled(self, state):
        if state: self.bantime.setEnabled(False);self.reason.setEnabled(False)
        else: self.bantime.setEnabled(True);self.reason.setEnabled(True)
    def on_chk_kick_2_toggled(self, state):
        if state: self.bantime_2.setEnabled(False);self.reason_2.setEnabled(False)
        else: self.bantime_2.setEnabled(True);self.reason_2.setEnabled(True)

    def on_chk_failover_stateChanged(self, state):
        if state == Qt.Checked: self.failoverBox.setEnabled(True)
        else: self.failoverBox.setEnabled(False)

    def on_toolButton_clicked(self):
        file = QFileDialog.getOpenFileName(self, "Select newline seperated ISP list", self.this.cfg['general']['isps'], "ISP List (*.*)")
        if file: self.this.cfg.set('main', 'isps', file)

    def on_btn_apply_clicked(self):
        try:
            self.this.cfg.set('general', 'debug', str(self.chk_debug.isChecked()))
            if self.chk_whitelist.isChecked(): self.this.cfg.set('general', 'whitelist', 'True')
            else: self.this.cfg.set('general', 'whitelist', 'False')
            if self.chk_kick.isChecked(): self.this.cfg.set('main', 'kickonly', 'True')
            else: self.this.cfg.set('main', 'kickonly', 'False')
            if self.chk_kick_2.isChecked(): self.this.cfg.set('failover', 'kickonly', 'True')
            else: self.this.cfg.set('failover', 'kickonly', 'False')
            self.this.cfg.set('main', 'bantime', str(self.bantime.value))
            self.this.cfg.set('failover', 'bantime', str(self.bantime_2.value))
            self.this.cfg.set('api', 'main', self.api_main.text)
            self.this.cfg.set('api', 'fallback', self.api_fallback.text)
            self.this.cfg.set('failover', 'enabled', str(self.chk_failover.isChecked()))
            for index in range(self.lst_events.count):
                item = self.lst_events.item(index)
                for event in self.this.cfg['events']:
                    if item.text().lower() == event: self.this.cfg.set('events', item.text(), str(item.checkState()==Qt.Checked))
            with open(self.this.ini, 'w') as configfile:
                self.this.cfg.write(configfile)
            self.close()
        except:
            ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
    def on_btn_cancel_clicked(self):
        self.close()
