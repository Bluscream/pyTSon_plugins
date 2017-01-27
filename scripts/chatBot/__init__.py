import ts3lib, ts3defines, datetime
from ts3plugin import ts3plugin
from pytsonui import setupUi
from PythonQt.QtGui import *
from PythonQt.QtCore import Qt
from configparser import ConfigParser
from os import path
from urllib.parse import quote as urlencode

class chatBot(ts3plugin):
    name = "Chat Bot"
    apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "A simply chatbot"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = False
    ini = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "chatBot", "settings.ini")
    cfg = ConfigParser()
    cmdini = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "chatBot", "commands.ini")
    cmd = ConfigParser()
    dlg = None

    def __init__(self):
        if path.isfile(self.ini): self.cfg.read(self.ini)
        else:
            self.cfg['general'] = { "cfgversion": "1", "debug": "False", "enabled": "True", "customprefix": "True", "prefix": "!" }
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        if path.isfile(self.cmdini): self.cmd.read(self.cmdini)
        else:
            self.cmd['time'] = { "enabled": "True", "function": "commandTime" }
            with open(self.cmdini, 'w') as configfile:
                self.cmd.write(configfile)
        ts3lib.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

    def configure(self, qParentWidget):
        try:
            if not self.dlg: self.dlg = SettingsDialog(self.ini, self.cfg, self.cmdini, self.cmd)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentiﬁer, message, ﬀIgnored):
        try:
            if ffIgnored: return False
            (error, _clid) = ts3.getClientID(schid)
            if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT and toID != _clid: return False
            #(error, _cid) = ts3.getChannelOfClient(schid, _clid)
            #if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL and toID != _cid: return False
            if message.startsWith(self.cfg.get('general', prefix)) and self.cfg.getboolean('general','customprefix'): command = message.split(self.cfg.get('general', prefix),1)[1]
            elif message.startsWith(self.clientURL(schid, _clid)) and self.cfg.getboolean('general','customprefix'): command = message.split(self.clientURL(schid, _clid),1)[1]
            else: return False
            ts3lib.printMessageToCurrentTab(command)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)



    def clientURL(self, schid=None, clid=0, uid=None, nickname=None, encodednick=None):
        if schid == None:
            try: schid = ts3.getCurrentServerConnectionHandlerID()
            except: pass
        if uid == None:
            try: (error, uid) = ts3.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            except: pass
        if nickname == None:
            try: (error, nickname) = ts3.getClientDisplayName(schid, clid)
            except: nickname = uid
        if encodednick == None:
            try: encodednick = urlencode(nickname)
            except: pass
        return "[url=client://%s/%s~%s]%s[/url]" % (clid, uid, encodednick, nickname)

class SettingsDialog(QDialog):
    def __init__(self, ini, cfg, cmdini, cmd, parent=None):
        self.ini = ini
        self.cfg = cfg
        self.cmdini = cmdini
        self.cmd = cmd
        super(QDialog, self).__init__(parent)
        setupUi(self, path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "chatBot", "settings.ui"))
        self.setWindowTitle("Chat Bot Settings")
        #header = self.tbl_commands.horizontalHeader()
        #header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        #header.setResizeMode(1, QtGui.QHeaderView.Stretch)
        #header.setResizeMode(2, QtGui.QHeaderView.Stretch)
        #self.tbl_commands.setColumnWidth(0, 25)
        self.chk_enabled.setChecked(cfg.getboolean("general", "enabled"))
        self.chk_debug.setChecked(cfg.getboolean("general", "debug"))
        self.grp_prefix.setChecked(cfg.getboolean("general", "customprefix"))
        self.txt_prefix.setText(cfg.get("general", "prefix"))
        self.loadCommands();
    def loadCommands(self):
        self.tbl_commands.clear()
        self.tbl_commands.setRowCount(len(self.cmd.sections()))
        row = 0
        for i in self.cmd.sections():
            item = QTableWidgetItem(i)
            kitem = QTableWidgetItem(self.cmd[i]["function"])
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            item.setCheckState(Qt.Checked if self.cmd.getboolean(i,"enabled") else Qt.Unchecked)
            self.tbl_commands.setItem(row, 1, kitem)
            self.tbl_commands.setItem(row, 0, item)
            row += 1
        self.tbl_commands.setRowCount(row)
        self.tbl_commands.sortItems(0)
    def on_btn_add_clicked(self):
        self.tbl_commands.insertRow(self.tbl_commands.rowCount()+1)
        #ok = BoolResult(); newurl = QInputDialog.getText(self, "Change url of repository %s" % name, "Url:", QLineEdit.Normal, rep["url"], ok)
        #if ok: rep["url"] = newurl
    def on_btn_remove_clicked(self):
        self.tbl_commands.removeRow(self.tbl_commands.selectedRows()[0])
    def on_btn_apply_clicked(self):
        ts3lib.printMessageToCurrentTab(str(self.grp_prefix.isChecked()))
        self.cfg.set('general', 'enabled', str(self.chk_enabled.isChecked()))
        self.cfg.set('general', 'debug', str(self.chk_debug.isChecked()))
        self.cfg.set('general', 'customprefix', str(self.grp_prefix.isChecked()))
        self.cfg.set('general', 'prefix', self.txt_prefix.text)
        with open(self.ini, 'w') as configfile: self.cfg.write(configfile)
        for i in self.tbl_commands.rowCount():
            try:
                if not self.tbl_commands.item(i,0).text() in self.cmd.sections(): self.cmd.add_section(i)
                self.cmd.set(self.tbl_commands.item(i,0).text(), "function", self.tbl_commands.item(i,1).text())
                self.cmd.set(self.tbl_commands.item(i,0).text(), "enabled", str(self.tbl_commands.item(i,0).isChecked()))
            except: ts3lib.logMessage("Could not add row %s to commands.ini"%i, ts3defines.LogLevel.LogLevel_INFO, "pyTSon Chat Bot", 0)
        with open(self.cmdini, 'w') as configfile: self.cmd.write(configfile)
        self.loadCommands();
    def on_btn_close_clicked(self):
        self.close()
