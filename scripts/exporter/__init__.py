from ts3plugin import ts3plugin, PluginHost
from ts3defines import *
import ts3lib
from pytson import getCurrentApiVersion
from PythonQt.QtCore import QTimer
from PythonQt.QtGui import QFileDialog, QDialog, QMessageBox
from bluscream import timestamp, msgBox, escapeStr
from ts3Ext import ts3SessionHost as ts3host



class exporter(ts3plugin):
    shortname = "EX"
    name = "Teamspeak Export/Import"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Like YaTQA, just as plugin.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = "ex"
    infoTitle = ""
    menuItems = [(PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Export Channel Tree", ""),
                (PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Import Channel Tree", "")]
    hotkeys = []
    ts3host = ts3host
    timer = QTimer
    # retcodes = []
    result = {"success": 0, "failed": 0, "total": 0, "msg": "", "stop": False}
    channels = []

    def __init__(self):
        if "aaa_ts3Ext" in PluginHost.active:
            ts3ext = PluginHost.active["aaa_ts3Ext"]
            self.ts3host = ts3ext.ts3host
            self.tabs = ts3ext.tabs
        else:
            self.timer.singleShot(500, self.__init__)
            return
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))


    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 1: self.importChannels(schid)
    def processCommand(self, schid, keyword):
        args = keyword.split(" ")
        cmd = args.pop(0).lower()
        if cmd == "import":
            subcmd = args.pop(0).lower()
            if subcmd == "channels":
                if len(args): self.importChannels(schid, args[0])
                else: self.importChannels(schid)
            else: return False
        elif cmd == "export": pass
        else: return False
        return True

    def readChannels(self, file):
        if not file: file = QFileDialog.getOpenFileName(QDialog(), "", "", "All Files (*);;YaTQA Exported Channels (*.ts3_chans)")
        channels = []
        with open(file) as fp:
            lines = fp.readlines()
            # i = 0
            for line in lines:
               if not line.strip(): continue # Todo: Maybe trycatch instead?
               line = line.rstrip().split("|", 1)
               _channel = line.pop(0).split(" ")
               channel = {"flags": {}}
               for pair in _channel:
                   pair = pair.split("=")
                   key = pair.pop(0)
                   (err, flag) = ts3lib.channelPropertyStringToFlag(key)
                   if err != ERROR_ok or not len(pair): continue
                   channel["flags"][flag] = escapeStr(pair.pop(0))
                   # ts3lib.printMessageToCurrentTab("{}: {} = {}".format(i, flag, value))
               if len(line):
                   perms = line.pop(0).split("|")
                   channel["permissions"] = []
                   for perm in perms:
                       permission = {}
                       perm = perm.split(" ")
                       for prop in perm:
                           prop = prop.split("=")
                           if prop[0] == "cid": continue
                           permission[prop[0]] = prop[1]
                           # print("{}: {} = {}".format(i, prop[0], prop[1]))
                       channel["permissions"].append(permission)
               channels.append(channel)
               # i += 1
        return channels
    def importChannels(self, schid, file=""):
        self.result = {"success": 0, "failed": 0, "total": 0, "msg": "", "stop": False}
        channels = self.readChannels(file)
        self.result["total"] = len(channels)
        for channel in channels:
            if self.result["stop"]:
                self.result["stop"] = False
                return
            for k, v in channel["flags"].items():
                ts3lib.setChannelVariableAsString(schid, 0, k, v)
                print("Setting var",k,"with value",v)
            returnCode = ts3lib.createReturnCode()
            # result = {}
            self.channels.append({returnCode: (channel["flags"][ChannelProperties.CHANNEL_NAME], channel["permissions"])})
            self.channels.append(channel)
            ts3lib.flushChannelCreation(schid, 0, returnCode)

    def onNewChannelCreatedEvent(self, serverConnectionHandlerID, channelID, channelParentID, invokerID, invokerName, invokerUniqueIdentifier):
        pass

    def onUpdateChannelEvent(self, serverConnectionHandlerID, channelID):
        pass


    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if not returnCode in self.channels: return False
        reason = "finished"; self.result["processed"] += 1
        if error == ERROR_ok:
            self.result["success"] += 1 # Todo Permissions
        elif error == ERROR_client_is_flooding:
            self.result["failed"] += 1; self.result["stop"] = True;reason = "stopped because of flooding"
        elif error in [ERROR_permissions_client_insufficient,ERROR_permissions_insufficient_group_power,ERROR_permissions_insufficient_permission_power]:
            self.result["failed"] += 1
        self.result["msg"] += "\n\"{}\": {}".format(self.channels[returnCode], reason)
        del self.channels[returnCode]
        if not len(self.channels):
            icon = QMessageBox.Error if self.result["failed"] else QMessageBox.Confirmation
            msgBox(self.result["msg"], icon, self.name)
        return True