# t = pluginhost.PluginHost.plugins["eventlog"]
import pytson, ts3client, ts3lib, ts3defines, pluginhost, re
from pytsonui import setupUi
from getvalues import getValues, ValueType
from PythonQt.QtCore import Qt
from PythonQt.QtGui import (QWidget, QTableWidgetItem, QHeaderView, QFont)
from ts3plugin import ts3plugin
from datetime import datetime
from configparser import ConfigParser
from os import path
import xml.etree.ElementTree as xml

class addonList(ts3plugin):
    name = "Addon Scanner"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "App Scanner like, just addons here"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = "[b]Addons[/b]:"
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "List Addons", "")]
    hotkeys = []
    ini = path.join(pytson.getPluginPath(), "scripts", "addonList", "settings.ini")
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
        self.setMeta(ts3lib.getCurrentServerConnectionHandlerID())
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.cfg.getboolean("general", "debug"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

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
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT and menuItemID == 0:
            try:
                (error, name) = ts3lib.getClientVariableAsString(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_NICKNAME)
                addons = self.parseMeta(schid,selectedItemID)
                if not self.dlg: self.dlg = AddonsDialog(addons, name, self.cfg)
                self.dlg.show()
                self.dlg.raise_()
                self.dlg.activateWindow()
            except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def infoData(self, schid, clid, atype): # https://github.com/teamspeak-plugins/now_playing/blob/master/now_playing/nowplaying_plugin.c#L667
        if atype == 2 and self.cfg.getboolean("general", "infodata"):
            i = []
            addons = self.parseMeta(schid, clid)
            try:
                pytsons = [element for element in addons.iter() if element.text == 'pyTSon']
                print("==========")
                print(xml.tostring(pytsons[0]).decode("utf-8"))
                print("==========")
                # xm = xml.fromstring('<element attribute="value">text<subelement subattribute="subvalue">subtext</subelement></element>')
                for pytson in pytsons:
                    scripts = pytson.findall("script")
                    i.append("[u]pyTSon[/u]:")
                    for script in scripts:
                        try: i.append("{name} v{version} by {author}".format(name=script.text,version=script.attrib["version"],author=script.attrib["author"]))
                        except:from traceback import format_exc;ts3lib.logMessage("Error parsing meta %s:\n%s"%(script.text,format_exc()), ts3defines.LogLevel.LogLevel_ERROR, "{c}.{f}".format(c=self.__class__,f=__name__), schid);continue
                # for name, plugin in pluginhost.PluginHost.plugins.items():
                #     try: i.append("{name} v{version} by {author}".format(name=plugin.name,version=plugin.version,author=plugin.author))
                #     except:
                #         if self.cfg.getboolean("general", "debug"): from traceback import format_exc;ts3lib.logMessage("Error listing {0}: {1}".format(plugin, format_exc()), ts3defines.LogLevel.LogLevel_ERROR, self.name, schid)
                #         continue
                return i
            except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0);pass

    def parseMeta(self, schid, clid):
        (error, meta) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_META_DATA)
        try: meta = re.search('<addons>(.+?)</addons>', meta).group(0)
        except AttributeError: return False
        return xml.fromstring(meta)


    def setMeta(self, schid, ownID=None):
        try:
            if ownID == None: (error, ownID) = ts3lib.getClientID(schid)
            (error, oldmeta) = ts3lib.getClientVariableAsString(schid, ownID, ts3defines.ClientProperties.CLIENT_META_DATA)
            # e = xml.etree.ElementTree.parse('<addons><pytson></pytson></addons>').getroot()
            if '<addons>' in oldmeta:
                oldmeta = re.sub(r"<addons>.*</addons>", "", oldmeta)
            newmeta = xml.Element('addons')
            db = ts3client.Config()
            q = db.query("SELECT value FROM addons")
            while(q.next()):
                val = q.value("value")
                addon = xml.SubElement(newmeta, "addon")
                for l in val.split('\n'):
                    try:
                        if l.startswith('name='):
                            name = l.split('=', 1)[1].strip()
                            addon.text = name
                        elif l.startswith('version='):
                            version = l.split('=', 1)[1].strip()
                            addon.set("version", version)
                        elif l.startswith('author='):
                            author = l.split('=', 1)[1].strip()
                            addon.set("author", author)
                        elif l.startswith('type='):
                            type = l.split('=', 1)[1].strip()
                            addon.set("type", type)
                    except:from traceback import format_exc;ts3lib.logMessage("Error reading addon from Database:\n%s"%(name,format_exc()), ts3defines.LogLevel.LogLevel_ERROR, "{c}.{f}".format(c=self.__class__,f=__name__), schid);continue
            del db
            pytson = [element for element in newmeta.iter() if element.text == 'pyTSon'][0]
            if self.cfg.getboolean("general", "activeonly"): plugins = pluginhost.PluginHost.active.items()
            else: plugins = pluginhost.PluginHost.plugins.items()
            for name, plugin in plugins:
                try:
                    script = xml.SubElement(pytson, "script",{'version': plugin.version, 'author': plugin.author})
                    script.text = name
                except:from traceback import format_exc;ts3lib.logMessage("Error parsing script %s:\n%s"%(name,format_exc()), ts3defines.LogLevel.LogLevel_ERROR, "{c}.{f}".format(c=self.__class__,f=__name__), schid);continue
            newmeta = "{old}{new}".format(old=oldmeta,new=xml.tostring(newmeta).decode("utf-8"))
            # if self.cfg.getboolean("general", "debug"): ts3lib.printMessageToCurrentTab(newmeta)
            error = ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_META_DATA, newmeta)
            if not error == ts3defines.ERROR_ok: ts3lib.printMessageToCurrentTab("Error: Unable to set own meta data to \"%s\"."%newmeta);return False
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "{c}.{f}".format(c=self.__class__,f=__name__), schid)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: self.setMeta(schid)

class AddonsDialog(QWidget):
    def __init__(self, addons, name, cfg, parent=None):
        try:
            super(QWidget, self).__init__(parent)
            setupUi(self, path.join(pytson.getPluginPath(), "scripts", "addonList", "addons.ui"))
            self.cfg = cfg
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("{0}'s Addons".format(name))
            self.txt_description.setVisible(False)
            self.tbl_addons.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.tbl_addons.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            self.setupList(addons.getchildren())
            self.resize(1000, 600)
            self.adddons = addons
        except:
            try: from traceback import format_exc;ts3lib.logMessage("addonList: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("addonList: "+format_exc())
                except: print("addonList: Unknown Error")

    def setupList(self, addons):
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
                    if self.cfg.getboolean("general", "debug"): ts3lib.printMessageToCurrentTab("%i [color=red]%s"%(row, xml.tostring(addon).decode("utf-8")))
                    try:
                        item = QTableWidgetItem(addon.attrib["version"])
                        item.setFlags(Qt.ItemIsEnabled | ~Qt.ItemIsEditable)
                        self.tbl_addons.setItem(row, 2, item)
                    except: ts3lib.logMessage("Addon %s does not have any version." % (addon.text), ts3defines.LogLevel.LogLevel_WARNING, "Addon List", 0)
                    try:
                        item = QTableWidgetItem(addon.attrib["author"])
                        item.setFlags(Qt.ItemIsEnabled | ~Qt.ItemIsEditable)
                        self.tbl_addons.setItem(row, 3, item)
                    except: ts3lib.logMessage("Addon %s does not have any author." % (addon.text), ts3defines.LogLevel.LogLevel_WARNING, "Addon List", 0)
                    row += 1
                except: from traceback import format_exc;ts3lib.logMessage("Error parsing addon %s:\n%s"%(addon.text,format_exc()), ts3defines.LogLevel.LogLevel_ERROR, "{c}.{f}".format(c=self.__class__,f=__name__), 0);continue
            self.tbl_addons.setRowCount(row)
            self.tbl_addons.sortItems(0)
            self.tbl_addons.setHorizontalHeaderLabels(["Type","Name","Version","Author","API"])
        except:
            try: from traceback import format_exc;ts3lib.logMessage("addonList: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
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
            try: from traceback import format_exc;ts3lib.logMessage("addonList: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("addonList: "+format_exc())
                except: print("addonList: Unknown Error")

    def on_btn_reload_clicked(self):
        try: self.setupList(self.adddons.getchildren())
        except:
            try: from traceback import format_exc;ts3lib.logMessage("addonList: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("addonList: "+format_exc())
                except: print("addonList: Unknown Error")

    def on_btn_description_clicked(self):
        try: self.txt_description.setVisible(not self.txt_description.visible)
        except:
            try: from traceback import format_exc;ts3lib.logMessage("addonList: "+format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            except:
                try: from traceback import format_exc;print("addonList: "+format_exc())
                except: print("addonList: Unknown Error")

    def on_btn_close_clicked(self): self.close()
