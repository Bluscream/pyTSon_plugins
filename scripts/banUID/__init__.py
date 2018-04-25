import ts3defines, ts3lib
from pytson import getPluginPath
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from os import path
from json import loads
from datetime import datetime
from pytsonui import setupUi
from getvalues import getValues, ValueType
from PythonQt.QtGui import QDialog, QComboBox
from PythonQt.QtCore import Qt, QUrl
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from bluscream import saveCfg, loadCfg, timestamp, msgBox
from configparser import ConfigParser
from traceback import format_exc

class banUID(ts3plugin):
    name = "Ban UID"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Requested by mrcraigtunstall"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Ban Client", "")]
    hotkeys = []
    ini = getPluginPath("scripts", "banUID", "config.ini")
    dlg = None
    cfg = ConfigParser()
    cfg["general"] = {
        "ip": "False",
        "name": "False",
        "uid": "True",
        "reason": "",
        "duration": "0",
        "template": ""
    }
    templates = {}

    def __init__(self):
        loadCfg(self.ini, self.cfg)
        url = self.cfg.get("general", "template")
        if url:
            self.nwmc = QNetworkAccessManager()
            self.nwmc.connect("finished(QNetworkReply*)", self.loadTemplates)
            self.nwmc.get(QNetworkRequest(QUrl(url)))
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def stop(self):
        saveCfg(self.ini, self.cfg)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT or menuItemID != 0: return
        (err, uid) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if err != ts3defines.ERROR_ok: uid = ""
        (err, name) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if err != ts3defines.ERROR_ok: name = ""
        (err, ip) = ts3lib.getConnectionVariable(schid, selectedItemID, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
        self.clid = selectedItemID
        if not ip: ip = "";ts3lib.requestConnectionInfo(schid, selectedItemID)
        if not self.dlg: self.dlg = BanDialog(self, schid, selectedItemID, uid, name, ip)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

    def onConnectionInfoEvent(self, schid, clid):
        if not hasattr(self, "clid") or clid != self.clid: return
        (err, ip) = ts3lib.getConnectionVariable(schid, clid, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
        if ip and self.dlg: self.dlg.txt_ip.setText(ip)
        del self.clid

    def loadTemplates(self, reply):
        data = reply.readAll().data().decode('utf-8')
        self.templates = loads(data)

class BanDialog(QDialog):
    def __init__(self, script, schid, clid, uid, name, ip, parent=None):
        super(QDialog, self).__init__(parent)
        setupUi(self, getPluginPath("scripts",script.__class__.__name__,"ban.ui"))
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Ban \"{}\" ({})".format(name, clid))
        self.grp_ip.setChecked(script.cfg.getboolean("general", "ip"))
        if ip: self.txt_ip.setText(ip)
        self.grp_name.setChecked(script.cfg.getboolean("general", "name"))
        if name: self.txt_name.setText(name)
        self.grp_uid.setChecked(script.cfg.getboolean("general", "uid"))
        if uid: self.txt_uid.setText(uid)
        for reason in script.templates: self.box_reason.addItem(reason)
        self.box_reason.setEditText(script.cfg.get("general", "reason")) # setItemText(0, )
        self.int_duration.setValue(script.cfg.getint("general", "duration"))
        self.cfg = script.cfg
        self.ini = script.ini
        self.schid = schid
        self.templates = script.templates

    def on_box_reason_currentTextChanged(self, text):
        if not text in self.templates: return
        self.int_duration.setValue(self.templates[text])

    def on_buttonBox_accepted(self):
        try:
            ip = self.txt_ip.text if self.grp_ip.isChecked() else ""
            name = self.txt_name.text if self.grp_name.isChecked() else ""
            uid = self.txt_uid.text if self.grp_uid.isChecked() else ""
            reason = self.box_reason.currentText # text
            duration = self.int_duration.value
            ts3lib.banadd(self.schid, ip, name, uid, duration, reason)
            # msgBox("schid: %s\nip: %s\nname: %s\nuid: %s\nduration: %s\nreason: %s"%(self.schid, ip, name, uid, duration, reason))
            self.cfg["general"] = {
                "ip": str(self.grp_ip.isChecked()),
                "name": str(self.grp_name.isChecked()),
                "uid": str(self.grp_uid.isChecked()),
                "reason": reason,
                "duration": str(duration)
            }
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)