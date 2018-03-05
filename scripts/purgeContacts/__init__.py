import ts3defines, ts3lib, ts3client
from ts3plugin import ts3plugin, PluginHost
from bluscream import *
from pytson import getPluginPath, getCurrentApiVersion
from os import path
from traceback import format_exc
from pytsonui import setupUi
from PythonQt.QtCore import Qt, QDate
from PythonQt.QtSql import QSqlDatabase
from PythonQt.QtGui import QDialog, QTableWidgetItem, QComboBox

class purgeContacts(ts3plugin):
    name = "Purge Contacts"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1"
    author = "Bluscream"
    description = "Allows you to clean your contact list "
    offersConfigure = False
    commandKeyword = ""
    infoTitle = ""
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, "")]
    hotkeys = []
    scriptpath = path.join(getPluginPath(), "scripts", "purgeContacts")
    dlg = None

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        self.dlg = calendarDialog(self)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

class calendarDialog(QDialog):
    def __init__(self, purgeContacts, parent=None):
        try:
            super(QDialog, self).__init__(parent)
            setupUi(self, path.join(purgeContacts.scriptpath, "calendar.ui"))
            self.setAttribute(Qt.WA_DeleteOnClose)
            # self.box_type.connect("currentIndexChanged(QString text)", self.box_type_currentIndexChanged)
            # self.buttonBox.connect("accepted()", self.accepted)
            self.purgeContacts = purgeContacts
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_box_type_currentIndexChanged(self, i):
        print("new index:", i)
        if i == 5: self.txt_filter.setEnabled(True)
        else: self.txt_filter.setEnabled(False)

    def on_buttonBox_accepted(self):
        dlg = calendarDialog(self.purgeContacts, self.box_type.currentText(), self.txt_filter.text(), self.calendarWidget.selectedDate())
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

class previewDialog(QDialog):
    def __init__(self, purgeContacts, filter, txt, date, parent=None):
        try:
            super(QDialog, self).__init__(parent)
            setupUi(self, path.join(purgeContacts.scriptpath, "preview.ui"))
            self.setAttribute(Qt.WA_DeleteOnClose)
            db = ts3client.Config()
            q = db.query("SELECT * FROM contacts")
            while q.next():
                contact = q.value("value").split('\n')
                """
                if line.startswith('Friend='):
                    status = int(line[-1])
                    if status == ContactStatus.FRIEND: buddies += 1
                    elif status == ContactStatus.BLOCKED: blocked += 1
                    elif status == ContactStatus.NEUTRAL: neutral += 1
                    else: unknown += 1
                elif line.lower().startswith('nickname=w/'):
                    female += 1
                elif line.lower().startswith('nickname=m/'):
                    male += 1
                """
            del db
            # self.setWindowTitle(self.windowTitle().format()) # TODO
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_buttonBox_accepted(self):
        pass