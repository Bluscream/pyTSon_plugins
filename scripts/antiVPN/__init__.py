import ts3defines, ts3lib
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QUrl, Qt
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from configparser import ConfigParser
from urllib.parse import quote as urlencode
from bluscream import getScriptPath, loadCfg, clientURL

class antiVPN(ts3plugin):
    path = getScriptPath(__name__)
    name = "Anti VPN"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Kicks users with VPNs"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    ini = "%s/config.ini"%path
    cfg = ConfigParser()
    cfg["general"] = {
        "cfgversion": "1",
        "enabled": "True",
        "api": "http://v2.api.iphub.info/ip/{ip}",
        "apikey": "Get yours at https://iphub.info/apiKey"
    }
    requested = {}

    def __init__(self):
        loadCfg(self.ini, self.cfg)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.cfg.getboolean("general", "enabled"): return
        if oldChannelID != 0: return
        (error, _type) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
        if _type == ts3defines.ClientType.ClientType_SERVERQUERY: return
        self.requested[schid] = [(schid, clid, "")]
        ts3lib.requestConnectionInfo(schid, clid)

    def onConnectionInfoEvent(self, schid, clientID):
        if not self.requested == clientID: return
        (error, ip) = ts3lib.getConnectionVariableAsString(schid, clientID, ts3defines.ConnectionProperties.CONNECTION_CLIENT_IP)
        if error == ts3defines.ERROR_ok:
            self.ip = ip
            self.nwm = QNetworkAccessManager()
            self.nwm.connect("finished(QNetworkReply*)", self.onMainReply)
            self.nwm.get(QNetworkRequest(QUrl(self.cfg['api']['main'].replace("{ip}",ip))))
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab(self.cfg['api']['main'].replace("{ip}",ip))
        else:
            (e, msg) = ts3lib.getErrorMessage(error)
            ts3lib.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the IP for '%s' (Reason: %s)" % (clientURL(schid, clientID),msg))

    def onMainReply(self, reply):
        if reply.error() == QNetworkReply.NoError:
            try:
                isp = reply.readAll().data().decode('utf-8')
                if isp.startswith('AS'): isp = isp.split(" ", 1)[1]
                if not isp or isp == "" or isp == "undefined":
                    ts3lib.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s) Falling back to %s" % (clientURL(self.schid, self.requested),format_exc(),self.cfg['api']['fallback'].replace("{ip}",self.ip)))
                    if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab(self.cfg['api']['fallback'].replace("{ip}",self.ip))
                    self.nwb = QNetworkAccessManager();self.nwb.connect("finished(QNetworkReply*)", self.onFallbackReply)
                    self.nwb.get(QNetworkRequest(QUrl(self.cfg['api']['fallback'].replace("{ip}",self.ip))));return
                if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("%s's ISP: %s"%(clientURL(self.schid, self.requested),isp))
                _match = False
                for _isp in self.isps:
                    if isp == _isp: _match = True
                if self.cfg.getboolean('general', 'whitelist') and not _match:
                    if self.cfg.getboolean('main', 'kickonly'):
                        ts3lib.requestClientKickFromServer(self.schid, self.requested, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                    else: ts3lib.banclient(self.schid, self.requested, 60, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                elif not self.cfg.getboolean('general', 'whitelist') and _match:
                    if self.cfg.getboolean('main', 'kickonly'):
                        ts3lib.requestClientKickFromServer(self.schid, self.requested, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                    else: ts3lib.banclient(self.schid, self.requested, 60, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
            except:
                try:
                    ts3lib.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s) Falling back to %s" % (clientURL(self.schid, self.requested),format_exc(),self.cfg['api']['fallback'].replace("{ip}",self.ip)))
                    if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab(self.cfg['api']['fallback'].replace("{ip}",self.ip))
                    self.nwb = QNetworkAccessManager();self.nwb.connect("finished(QNetworkReply*)", self.onFallbackReply)
                    self.nwb.get(QNetworkRequest(QUrl(self.cfg['api']['fallback'].replace("{ip}",self.ip))))
                except: pass
        else:
            ts3lib.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s) Falling back to %s" % (clientURL(self.schid, self.requested),reply.errorString(),self.cfg['api']['fallback'].replace("{ip}",self.ip)))
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab(self.cfg['api']['fallback'].replace("{ip}",self.ip))
            self.nwb = QNetworkAccessManager();self.nwb.connect("finished(QNetworkReply*)", self.onFallbackReply)
            self.nwb.get(QNetworkRequest(QUrl(self.cfg['api']['fallback'].replace("{ip}",self.ip))))
        reply.deleteLater()

    def onFallbackReply(self, reply):
        if reply.error() == QNetworkReply.NoError:
            try:
                isp = reply.readAll().data().decode('utf-8')
                if isp.startswith('AS'): isp = isp.split(" ", 1)[1]
                if not isp or isp == "" or isp == "undefined":
                    ts3lib.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s)" % (clientURL(self.schid, self.requested),format_exc()))
                    if self.cfg.getboolean("failover", "enabled"):
                        if self.cfg.getboolean('failover', 'kickonly'):
                            ts3lib.requestClientKickFromServer(self.schid, self.requested, self.cfg['failover']['reason'].replace('{isp}', isp));
                        else: ts3lib.banclient(self.schid, self.requested, int(self.cfg['failover']['bantime']), self.cfg['failover']['reason'].replace('{isp}', isp))
                        self.requested = 0;reply.deleteLater();return
                if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("%s's ISP: %s"%(clientURL(self.schid, self.requested),isp))
                _match = False
                for _isp in self.isps:
                    if isp == _isp: _match = True
                if self.cfg.getboolean('general', 'whitelist') and not _match:
                    if self.cfg.getboolean('main', 'kickonly'):
                        ts3lib.requestClientKickFromServer(self.schid, self.requested, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                    else: ts3lib.banclient(self.schid, self.requested, 60, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                elif not self.cfg.getboolean('general', 'whitelist') and _match:
                    if self.cfg.getboolean('main', 'kickonly'):
                        ts3lib.requestClientKickFromServer(self.schid, self.requested, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
                    else: ts3lib.banclient(self.schid, self.requested, 60, "%s is not a valid Internet Service Provider!" % isp);self.requested = 0
            except:
                ts3lib.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s)" % (clientURL(self.schid, self.requested),""))
                if self.cfg.getboolean("failover", "enabled"):
                    if self.cfg.getboolean('failover', 'kickonly'):
                        ts3lib.requestClientKickFromServer(self.schid, self.requested, self.cfg['failover']['reason'].replace('{isp}', isp));
                    else: ts3lib.banclient(self.schid, self.requested, int(self.cfg['failover']['bantime']), self.cfg['failover']['reason'].replace('{isp}', isp))
        else:
            ts3lib.printMessageToCurrentTab("[[color=orange]WARNING[/color]] [color=red]ISPValidator could not resolve the ISP for '%s' (Reason: %s)" % (clientURL(self.schid, self.requested),reply.errorString()))
            if self.cfg.getboolean("failover", "enabled"):
                if self.cfg.getboolean('failover', 'kickonly'):
                    ts3lib.requestClientKickFromServer(self.schid, self.requested, self.cfg['failover']['reason'].replace('{isp}', isp));
                else: ts3lib.banclient(self.schid, self.requested, int(self.cfg['failover']['bantime']), self.cfg['failover']['reason'].replace('{isp}', isp))
        self.requested = 0
        reply.deleteLater()