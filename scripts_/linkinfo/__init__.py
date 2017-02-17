from ts3plugin import ts3plugin
import ts3lib as ts3
import ts3defines, os.path
from os import path
from PythonQt.QtSql import QSqlDatabase
from PythonQt.QtGui import *
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from pytsonui import *
from traceback import format_exc


class Linkinfo(ts3plugin):
    name = "Linkinfo"
    requestAutoload = False
    version = "1.0.1"
    apiVersion = 21
    author = "Luemmel"
    description = "Prints a Linkinfolink to the chat."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Linkinfo settings", "")]
    directory = path.join(ts3.getPluginPath(), "pyTSon", "scripts", "linkinfo")
    protocols = []
    domains = []
    status = True
    mode = False
    wotapikey = "7132a9b89377c75f81f2ef87aa10896da7c28544" #

    def __init__(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE", "pyTSon_linkinfo")
        self.db.setDatabaseName(path.join(self.directory, "linkinfo.db"))
        if not self.db.isValid():
            raise Exception("Database invalid")
        if not self.db.open():
            raise Exception("Could not open database.")
        d = self.db.exec_("SELECT * FROM domains ORDER BY domain ASC")
        while d.next():
            self.domains.append(str(d.value("domain")))
        p = self.db.exec_("SELECT * FROM protocols ORDER BY protocol ASC")
        while p.next():
            self.protocols.append(str(p.value("protocol")))
        s = self.db.exec_("SELECT * FROM settings")
        if s.next():
            self.status = bool(s.value("status"))
            self.mode = bool(s.value("mode"))
        self.dlg = None

    def stop(self):
        self.db.close()
        self.db.delete()
        QSqlDatabase.removeDatabase("pyTSon_linkinfo")

    def configure(self, qParentWidget):
        self.open_dlg()

    def onMenuItemEvent(self, sch_id, a_type, menu_item_id, selected_item_id):
        if a_type == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menu_item_id == 0:
                self.open_dlg()

    def open_dlg(self):
        if not self.dlg:
            self.dlg = SettingsDialog(self)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
        return True

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if self.status:
            (error, myid) = ts3.getClientID(schid)
            message = message.lower()
            if not myid == fromID and ("[url]" in message or "[url=" in message):
                domain_whitelisted = False
                for protocol in self.protocols:
                    if protocol+"://" in message:
                        domain_whitelisted = True
                for domain in self.domains:
                    if "[url]http://"+domain in message or "[url]https://"+domain in message:
                        domain_whitelisted = True
                    if "[url=http://"+domain in message or "[url=https://"+domain in message:
                        domain_whitelisted = True
                    if "[url]http://www."+domain in message or "[url]https://www."+domain in message:
                        domain_whitelisted = True
                    if "[url=http://www."+domain in message or "[url=https://www."+domain in message:
                        domain_whitelisted = True
                    if "[url]www."+domain in message or "[url=www."+domain in message:
                        domain_whitelisted = True
                if not domain_whitelisted:
                    start = message.find("[url]")
                    if not start == -1:
                        end = message.find("[/url]")
                        message = message[start + 5:end]
                    else:
                        start = message.find("[url=")
                        end = message.find("]")
                        message = message[start + 5:end]
                    self.getLinkInfo([message])
                    message = "[[url=http://www.getlinkinfo.com/info?link=" + message + "]Linkinfo[/url]] "+message
                    if self.mode:
                        if targetMode == 1:
                            ts3.requestSendPrivateTextMsg(schid, message, fromID)
                        if targetMode == 2:
                            (error, mych) = ts3.getChannelOfClient(schid, myid)
                            ts3.requestSendChannelTextMsg(schid, message, mych)
                    else:
                        ts3.printMessageToCurrentTab(str(message))

    def getLinkInfo(self, urls): # https://www.mywot.com/wiki/API
        links = "/".join(urls)
        print(links)
        url = "http://api.mywot.com/0.4/public_link_json2?hosts=%s&callback=process&key=%s" % (links,self.wotapikey)
        ts3.logMessage('Requesting %s'%url, ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Linkinfo Script", 0)
        self.nwm = QNetworkAccessManager()
        self.nwm.connect("finished(QNetworkReply*)", self.onNetworkReply)
        self.nwm.get(QNetworkRequest(QUrl(url)))

    def onNetworkReply(self, reply):
        if reply.error() == QNetworkReply.NoError:
            try:
                response = reply.readAll().data().decode('utf-8')
                ts3.printMessageToCurrentTab(response)
            except:
                ts3.printMessageToCurrentTab(format_exc())

class SettingsDialog(QDialog):
    def __init__(self, linkinfo, parent=None):
        self.li = linkinfo
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "linkinfo", "linkinfo.ui"))
        self.setWindowTitle("Linkinfo by Luemmel")
        self.btn_add_domain.clicked.connect(self.add_domain)
        self.btn_remove_domain.clicked.connect(self.remove_domain)
        self.btn_add_protocol.clicked.connect(self.add_protocol)
        self.btn_remove_protocol.clicked.connect(self.remove_protocol)
        self.cb_status.stateChanged.connect(self.toggle_status)
        self.cb_mode.stateChanged.connect(self.toggle_mode)

        self.pixmap = QPixmap(os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "linkinfo", "luemmel.png"))
        self.pixmap.scaledToWidth(110)
        self.label_image.setPixmap(self.pixmap)

        self.cb_status.setChecked(linkinfo.status)
        self.cb_mode.setChecked(linkinfo.mode)
        self.list_domain.addItems(linkinfo.domains)
        self.list_protocol.addItems(linkinfo.protocols)

    def toggle_status(self):
        if self.cb_status.isChecked():
            self.li.db.exec_("UPDATE settings SET status = 1")
            self.li.status = True
        else:
            self.li.db.exec_("UPDATE settings SET status = 0")
            self.li.status = False

    def toggle_mode(self):
        if self.cb_mode.isChecked():
            self.li.db.exec_("UPDATE settings SET mode = 1")
            self.li.mode = True
        else:
            self.li.db.exec_("UPDATE settings SET mode = 0")
            self.li.mode = False

    def add_domain(self):
        text = self.input_text_domain.toPlainText().lower()
        if text not in self.li.domains:
            self.li.db.exec_("INSERT INTO domains (domain) VALUES ('"+text+"')")
            self.li.domains.append(text)
            self.li.domains.sort()
            self.list_domain.clear()
            self.list_domain.addItems(self.li.domains)

    def remove_domain(self):
        selected_item = self.list_domain.currentItem().text()
        self.li.db.exec_("DELETE FROM domains WHERE domain = '"+selected_item+"'")
        self.li.domains.remove(selected_item)
        self.list_domain.clear()
        self.list_domain.addItems(self.li.domains)

    def add_protocol(self):
        text = self.input_text_protocol.toPlainText().lower()
        if text not in self.li.protocols:
            self.li.db.exec_("INSERT INTO protocols (protocol) VALUES ('" + text + "')")
            self.li.protocols.append(text)
            self.li.protocols.sort()
            self.list_protocol.clear()
            self.list_protocol.addItems(self.li.protocols)

    def remove_protocol(self):
        selected_item = self.list_protocol.currentItem().text()
        self.li.db.exec_("DELETE FROM protocols WHERE protocol = '" + selected_item + "'")
        self.li.protocols.remove(selected_item)
        self.list_protocol.clear()
        self.list_protocol.addItems(self.li.protocols)
