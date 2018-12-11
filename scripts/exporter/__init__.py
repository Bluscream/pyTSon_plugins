from ts3plugin import ts3plugin, PluginHost
from datetime import datetime
import ts3lib, ts3defines
from pytson import getCurrentApiVersion
from PythonQt.QtCore import QTimer
from PythonQt.QtGui import QFileDialog, QDialog
from bluscream import timestamp
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
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Export Channel Tree", ""),
                (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Import Channel Tree", "")]
    hotkeys = []
    ts3host = ts3host
    timer = QTimer

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
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
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

    def importChannels(self, schid, file=""):
        if not file: file = QFileDialog.getOpenFileName(QDialog(), "", "", "All Files (*);;YaTQA Exported Channels (*.ts3_chans)")
        channels = []
        with open(file) as fp:
            lines = fp.readlines()
            i = 0
            for line in lines:
               line = line.rstrip().split('|', 1)
               channel = line.pop(0).split(" ")
               for pair in channel:
                   pair = pair.split("=")
                   key = pair.pop(0)
                   (err, flag) = ts3lib.channelPropertyStringToFlag(key)
                   value = pair.pop(0) if len(pair) else ""
                   # ts3lib.printMessageToCurrentTab("{}: {} = {}".format(i, flag, value))
               if len(line):
                   perms = line.pop(0).split("|")
                   for perm in perms:
                       perm = perm.split(" ")
                       for perm in perm
               i += 1