import pytson, ts3client, ts3defines, pluginhost, re
import ts3lib as ts3
from pytsonui import setupUi
from getvalues import getValues, ValueType
from PythonQt.QtCore import Qt
from PythonQt.QtGui import QWidget, QDialog, QTableWidgetItem, QHeaderView, QFont
from ts3plugin import ts3plugin
from datetime import datetime
from configparser import ConfigParser
from os import path

class dataDump(ts3plugin):
    name = "Data Dump"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Dump any data"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Data Dumps", "")]
    hotkeys = []
    ini = path.join(pytson.getPluginPath(), "scripts", "dataDump", "settings.ini")
    cfg = ConfigParser()
    dlg = None

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = {"cfgversion": "1", "debug": "False", "enabled": "True", "infodata": "False", "activeonly": "False"}
            with open(self.ini, 'w') as cfg:
                self.cfg.write(cfg)
        schid = ts3.getCurrentServerConnectionHandlerID()
        err, ownid = ts3.getClientID(schid)
        if not err: self.setMeta(ts3.getCurrentServerConnectionHandlerID())
        if self.cfg.getboolean("general", "debug"): ts3.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def configure(self, qParentWidget):
        try:
            d = dict()
            for n, v in self.cfg['general'].items():
                if n == "cfgversion": continue
                d[n] = (ValueType.boolean, n.title(), self.cfg.getboolean('general', n), None, None)
            getValues(qParentWidget, self.name, d, self.configDialogClosed)
        except: from traceback import format_exc;ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def configDialogClosed(self, r, vals):
        try:
            if r == QDialog.Accepted:
                for n, v in vals.items():
                    try:
                        if not v == self.cfg.getboolean('general', n):
                            self.cfg.set('general', n, str(v))
                    except: from traceback import format_exc;ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
                with open(self.ini, 'w') as configfile:
                    self.cfg.write(configfile)
        except: from traceback import format_exc;ts3.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            if not self.dlg: self.dlg = DumpView()
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: self.setMeta(schid)

class DumpView(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        setupUi(self, path.join(pytson.getPluginPath(), "scripts", "dataDump", "dump.ui"))
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Version Dumps")
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        # self.setupTable()
        self.resize(800, 600)

    def setupTable(self, addons=None):
        try:
            self.tbl_addons.clear()
            self.tbl_addons.setRowCount(len(addons))
            row = 0
            for addon in addons:
                try:
                    if addon == None or addon.text == None: continue
                    _type = "Other";
                    try:
                        _type = addon.attrib["type"].title()
                    except: pass
                    item = QTableWidgetItem(_type)
                    item.setFlags(Qt.ItemIsEnabled | ~Qt.ItemIsEditable)
                    self.tbl_addons.setItem(row, 0, item)
                    item = QTableWidgetItem(addon.text)
                    if len(list(addon)):
                        font = QFont()
                        font.setBold(True)
                        item.setFont(font)
                        # item.setData(Qt.UserRole, addon.text)
                        if addon.text == "pyTSon": self.pytson = addon
                        elif addon.text == "Lua": self.lua = addon
                    item.setFlags(Qt.ItemIsEnabled | ~Qt.ItemIsEditable)
                    self.tbl_addons.setItem(row, 1, item)
                    if self.cfg.getboolean("general", "debug"): ts3.printMessageToCurrentTab("%i [color=red]%s"%(row, xml.tostring(addon).decode("utf-8")))
                    try:
                        item = QTableWidgetItem(addon.attrib["version"])
                        item.setFlags(Qt.ItemIsEnabled | ~Qt.ItemIsEditable)
                        self.tbl_addons.setItem(row, 2, item)
                    except: ts3.logMessage("Addon %s does not have any version." % (addon.text), ts3defines.LogLevel.LogLevel_WARNING, "Addon List", 0)
                    try:
                        item = QTableWidgetItem(addon.attrib["author"])
                        item.setFlags(Qt.ItemIsEnabled | ~Qt.ItemIsEditable)
                        self.tbl_addons.setItem(row, 3, item)
                    except: ts3.logMessage("Addon %s does not have any author." % (addon.text), ts3defines.LogLevel.LogLevel_WARNING, "Addon List", 0)
                    row += 1
                except: from traceback import format_exc;ts3.logMessage("Error parsing addon %s:\n%s"%(addon.text,format_exc()), ts3defines.LogLevel.LogLevel_ERROR, "{c}.{f}".format(c=self.__class__,f=__name__), 0);continue
            self.tbl_addons.setRowCount(row)
            self.tbl_addons.sortItems(0)
            self.tbl_addons.setHorizontalHeaderLabels(["Type","Name","Version","Author","API"])
        except:
            try: from traceback import format_exc;ts3.logMessage("addonList: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("addonList: "+format_exc())
                except: print("addonList: Unknown Error")

    def on_tbl_addons_doubleClicked(self, mi):
        try:
            row = self.tbl_addons.currentRow()
            data = self.tbl_addons.item(row,1).text()
            if data == "pyTSon": self.setupList(self.pytson.getchildren())
            elif data == "Lua": self.setupList(self.lua.getchildren())
        except:
            try: from traceback import format_exc;ts3.logMessage("addonList: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("addonList: "+format_exc())
                except: print("addonList: Unknown Error")

    def on_btn_reload_clicked(self):
        try: self.setupList(self.adddons.getchildren())
        except:
            try: from traceback import format_exc;ts3.logMessage("addonList: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("addonList: "+format_exc())
                except: print("addonList: Unknown Error")

    def on_btn_description_clicked(self):
        try: self.txt_description.setVisible(not self.txt_description.visible)
        except:
            try: from traceback import format_exc;ts3.logMessage("addonList: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("addonList: "+format_exc())
                except: print("addonList: Unknown Error")

    def on_btn_close_clicked(self): self.close()
