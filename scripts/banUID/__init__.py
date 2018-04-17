import ts3defines, ts3lib
from pytson import getPluginPath
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from os import path
from datetime import datetime
from pytsonui import setupUi
from getvalues import getValues, ValueType
from PythonQt.QtGui import QDialog
from PythonQt.QtCore import Qt
from bluscream import saveCfg, loadCfg, timestamp, msgBox
from configparser import ConfigParser

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
        "duration": "-1"
    }

    def __init__(self):
        loadCfg(self.ini, self.cfg)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def stop(self):
        saveCfg(self.ini, self.cfg)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT or menuItemID != 0: return
        (err, uid) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        (err, name) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        (err, ip) = ts3lib.getConnectionVariable(schid, selectedItemID, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
        self.clid = selectedItemID
        if not ip: ts3lib.requestConnectionInfo(schid, selectedItemID)
        if not self.dlg: self.dlg = BanDialog(self, schid, selectedItemID, uid, name, ip)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

    def onConnectionInfoEvent(self, schid, clid):
        if not self.clid or clid != self.clid: return
        (err, ip) = ts3lib.getConnectionVariable(schid, clid, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
        if ip and self.dlg: self.dlg.txt_ip.setText(ip)
        del self.clid


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
        self.txt_reason.setText(script.cfg.get("general", "reason"))
        self.int_duration.setValue(script.cfg.getint("general", "duration"))
        self.cfg = script.cfg
        self.ini = script.ini
        self.schid = schid

    def on_buttonBox_accepted(self):
        ip = self.txt_ip.text if self.grp_ip.isChecked() else ""
        name = self.txt_name.text if self.grp_name.isChecked() else ""
        uid = self.txt_uid.text if self.grp_uid.isChecked() else ""
        reason = self.txt_reason.text
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