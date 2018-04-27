import ts3defines, ts3lib, re
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from ts3client import CountryFlags
from os import path
from json import loads
from datetime import datetime
from pytsonui import setupUi
from getvalues import getValues, ValueType
from PythonQt.QtGui import QDialog, QComboBox
from PythonQt.QtCore import Qt, QUrl
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from bluscream import saveCfg, loadCfg, timestamp, getScriptPath, confirm #, percent
from configparser import ConfigParser
from traceback import format_exc

class customBan(ts3plugin):
    path = getScriptPath(__name__)
    name = "Custom Ban"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Requested by @mrcraigtunstall (217.61.6.128)\nExtended for @SossenSystems (ts3public.de)"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Ban Client", "scripts/%s/ban_client.svg"%__name__)]
    hotkeys = []
    ini = "%s/config.ini"%path
    dlg = None
    cfg = ConfigParser()
    cfg["general"] = { "template": "", "whitelist": "", "ipapi": "True" } # , "http://ip-api.com/json/{ip}"
    cfg["last"] = {
        "ip": "False",
        "name": "False",
        "uid": "True",
        "reason": "",
        "duration": "0"
    }
    templates = {}
    whitelist = ["127.0.0.1"]

    def __init__(self):
        loadCfg(self.ini, self.cfg)
        url = self.cfg.get("general", "template")
        if url:
            self.nwmc_template = QNetworkAccessManager()
            self.nwmc_template.connect("finished(QNetworkReply*)", self.loadTemplates)
            self.nwmc_template.get(QNetworkRequest(QUrl(url)))
        url = self.cfg.get("general", "whitelist")
        if url:
            self.nwmc_whitelist = QNetworkAccessManager()
            self.nwmc_whitelist.connect("finished(QNetworkReply*)", self.loadWhitelist)
            self.nwmc_whitelist.get(QNetworkRequest(QUrl(url)))
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
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.name, "> Downloaded ban templates:", self.templates)

    def loadWhitelist(self, reply):
        data = reply.readAll().data().decode('utf-8')
        self.whitelist = []
        pat_ipv4 = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        for line in data.splitlines():
            if re.match(pat_ipv4, line): self.whitelist.append(line.strip())
            else: print(self.name,">",line,"is not a valid IP! Not adding to whitelist.")
        # self.whitelist = [s.strip() for s in data.splitlines()]
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.name, "> Downloaded ip whitelist:", self.whitelist)

class BanDialog(QDialog):
    def __init__(self, script, schid, clid, uid, name, ip, parent=None):
        try:
            super(QDialog, self).__init__(parent)
            setupUi(self, "%s/ban.ui"%script.path)
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Ban \"{}\" ({})".format(name, clid))
            self.lbl_flag.setVisible(False)
            url = script.cfg.getboolean("general", "ipapi")
            if url:
                self.nwmc_ip = QNetworkAccessManager()
                self.nwmc_ip.connect("finished(QNetworkReply*)", self.checkIP)
                self.countries = CountryFlags()
                self.countries.open()
            else: self.lbl_isp.setVisible(False); self.txt_isp.setVisible(False); self.txt_loc.setVisible(False)
            self.grp_ip.setChecked(script.cfg.getboolean("last", "ip"))
            if ip: self.txt_ip.setText(ip)
            self.grp_name.setChecked(script.cfg.getboolean("last", "name"))
            if name: self.txt_name.setText(name)
            self.grp_uid.setChecked(script.cfg.getboolean("last", "uid"))
            if uid: self.txt_uid.setText(uid)
            for reason in script.templates: self.box_reason.addItem(reason)
            self.box_reason.setEditText(script.cfg.get("last", "reason")) # setItemText(0, )
            self.int_duration.setValue(script.cfg.getint("last", "duration"))
            self.cfg = script.cfg
            self.ini = script.ini
            self.schid = schid
            self.templates = script.templates
            self.whitelist = script.whitelist
            self.name = script.name
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0); pass

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
            if ip:
                check = True
                if len(self.whitelist) < 1: check = confirm("Empty IP Whitelist!", "The IP whitelist is empty! Are you sure you want to ban \"{}\"?\n\nMake sure your whitelist URL\n{}\nis working!".format(ip, self.cfg.get("general", "whitelist")))
                if ip in self.whitelist: ts3lib.printMessageToCurrentTab("{}: [color=red]Not banning whitelisted IP [b]{}".format(self.name, ip))
                elif check: ts3lib.banadd(self.schid, ip, "", "", duration, reason)
            if name: ts3lib.banadd(self.schid, "", name, "", duration, reason)
            if uid: ts3lib.banadd(self.schid, "", "", uid, duration, reason)
            # msgBox("schid: %s\nip: %s\nname: %s\nuid: %s\nduration: %s\nreason: %s"%(self.schid, ip, name, uid, duration, reason))
            self.cfg["last"] = {
                "ip": str(self.grp_ip.isChecked()),
                "name": str(self.grp_name.isChecked()),
                "uid": str(self.grp_uid.isChecked()),
                "reason": reason,
                "duration": str(duration)
            }
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_txt_ip_textChanged(self, text):
        try:
            if not hasattr(self, "nwmc_ip"): return
            if not text: return
            if not re.match('^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', text): return
            if text.strip() in ["127.0.0.1", "0.0.0.0", "255.255.255"]: return
            self.nwmc_ip.get(QNetworkRequest(QUrl("http://ip-api.com/json/{ip}".format(ip=text))))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def checkIP(self, reply):
        try:
            data = loads(reply.readAll().data().decode('utf-8'))
            if PluginHost.cfg.getboolean("general", "verbose"): print(self.name, "> Resolved IP ", self.txt_ip.text,":", data)
            if data["status"] == "success": self.txt_loc.setVisible(True)
            else: self.txt_isp.setText(data["status"]); self.txt_loc.setVisible(False); return
            self.txt_isp.setText(data["isp"])
            self.txt_loc.setText("{}, {}, {}".format(data["city"], data["regionName"], data["country"]))
            if hasattr(data, "countryCode") and data["countryCode"]:
                self.lbl_flag.setPixmap(self.countries.flag(data["countryCode"]))
                self.lbl_flag.setVisible(True)
            else: self.lbl_flag.setVisible(False)
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)