from PythonQt.QtCore import QProcess, QUrl
from PythonQt.QtGui import QDesktopServices
from os.path import isfile
from ts3plugin import ts3plugin
from pluginhost import PluginHost
from bluscream import timestamp, getScriptPath, msgBox, inputInt, inputBox
import ts3defines, ts3lib, pytson

class YaTQA(ts3plugin):
    path = getScriptPath(__name__)
    name = "YaTQA"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Script to utilize YaTQA"
    offersConfigure = False
    commandKeyword = "yatqa"
    infoTitle = None
    hotkeys = [
        # ("yatqa_start", "Start YaTQA"),
        ("yatqa_connect_current", "Start YaTQA and connect to current server"),
        ("yatqa_stats_current", "Start YaTQA and check stats"),
        ("yatqa_blacklist_current", "Start YaTQA and check if current server is blacklisted"),
        ("yatqa_lookup_dns", "Start YaTQA and lookup (TS)DNS"),
        ("yatqa_browse_icons", "Start YaTQA and view local icons"),
        ("yatqa_permission_editor", "Start YaTQA and open permission editor"),
        ("yatqa_connect_default", "Start YaTQA and connect to default server"),
    ]
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "== {0} ==".format(name),""),
        # (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Start YaTQA", "scripts/%s/yatqa.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "Connect to current", "scripts/%s/yatqa.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 3, "Statistics", "scripts/%s/stats.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 4, "Blacklist", "scripts/%s/blacklist_check.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 5, "Lookup (TS)DNS", "scripts/%s/dns.png"%__name__),
        # (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 6, "View Icons", "scripts/%s/icons.png"%__name__),
        # (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 7, "Permission Editor", "scripts/%s/permission_editor.png"%__name__),
        # (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 8, "Connect to default", "scripts/%s/default.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 10, "== {0} ==".format(name),"")
    ]
    yatqa = QProcess()
    lastpass = {}
    bin = "C:/Program Files (x86)/YaTQA/yatqa.exe"
    autoBlackListCheck = False

    def __init__(self):
        if isfile(self.bin):
            self.yatqa = QProcess()
            self.yatqa.setProgram(self.bin)
        else:
            msgBox("Cannot find YatQA!\nPlease make sure it's installed at\n\n\"{}\"".format(self.bin))
            QDesktopServices.openUrl(QUrl("http://yat.qa/"))
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def menuCreated(self):
        if not self.name in PluginHost.active: return
        for id in [0,10]:
            try: ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, id), False)
            except: pass

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL: return False
        keyword = ""
        if menuItemID == 1: keyword = "yatqa_start"
        elif menuItemID == 2: keyword = "yatqa_connect_current"
        elif menuItemID == 3: keyword = "yatqa_stats_current"
        elif menuItemID == 4: keyword = "yatqa_blacklist_current"
        elif menuItemID == 5: keyword = "yatqa_lookup_dns"
        elif menuItemID == 6: keyword = "yatqa_browse_icons"
        elif menuItemID == 7: keyword = "yatqa_permission_editor"
        elif menuItemID == 8: keyword = "yatqa_connect_default"
        else: return
        self.onHotkeyOrCommandEvent(keyword, schid)

    def processCommand(self, schid, keyword): return self.onHotkeyOrCommandEvent(keyword, schid)
    def onHotkeyEvent(self, keyword): return self.onHotkeyOrCommandEvent(keyword)
    def onHotkeyOrCommandEvent(self, keyword, schid=0):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        # (err, status) = ts3lib.getConnectionStatus(schid)
        # if status != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        arguments = []
        if keyword == "yatqa_start": pass
        elif keyword == "yatqa_connect_current":
            (err, ownID) = ts3lib.getClientID(schid)
            (err, ip) = ts3lib.getConnectionVariable(schid, ownID, ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
            (err, port) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_PORT)
            title = ("{} > {}".format(self.name, ip))
            qport = inputInt(title, "Query Port:",10011,1,65535)
            name = inputBox(title, "Query Login Name:","serveradmin")
            pw = inputBox(title, "Query Login Password:", self.lastpass[schid] if schid in self.lastpass else "")
            args = ["-c", ip, qport]
            if name and pw: args.extend([name, pw, port])
            else: args.append(port)
            self.yatqa.setArguments(args) # IP Query_Port [User Pass] [Voice_Port]
        elif keyword == "yatqa_stats_current":
            (err, ownID) = ts3lib.getClientID(schid)
            (err, ip) = ts3lib.getConnectionVariable(schid, ownID, ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
            (err, port) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_PORT)
            self.yatqa.setArguments(["-s", ip, port]) # IP
        elif keyword == "yatqa_blacklist_current":
            (err, ownID) = ts3lib.getClientID(schid)
            (err, ip) = ts3lib.getConnectionVariable(schid, ownID, ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
            self.yatqa.setArguments(["-b", ip]) # IP
        elif keyword == "yatqa_lookup_dns":
            (err, host, port, pw) = ts3lib.getServerConnectInfo(schid)
            self.yatqa.setArguments(["-d", host])
        elif keyword == "yatqa_browse_icons":
            (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
            self.yatqa.setArguments(["-i", suid])
        elif keyword == "yatqa_permission_editor":
            self.yatqa.setArguments(["-p"])
        elif keyword == "yatqa_connect_default":
            self.yatqa.setArguments(["-a"])
        else: return False
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.bin, self.yatqa.arguments())
        self.yatqa.start()
        return True

    def onClientServerQueryLoginPasswordEvent(self, schid, loginPassword):
        self.lastpass[schid] = loginPassword
        ts3lib.printMessage(schid, "Created new query login password: {}".format(loginPassword), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if not self.autoBlackListCheck: return
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        (err, ownID) = ts3lib.getClientID(schid)
        (err, ip) = ts3lib.getConnectionVariable(schid, ownID, ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
        self.yatqa.setArguments(["-b", ip])
        self.yatqa.start()