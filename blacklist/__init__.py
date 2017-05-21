from ts3plugin import ts3plugin, PluginHost
from ts3lib import getPluginPath
from os import path
import ts3defines,  pickle, re, pytson, ts3lib
from PythonQt.QtSql import QSqlDatabase
from PythonQt.QtGui import *
from PythonQt.QtCore import Qt
from pytsonui import *


class Blacklist(ts3plugin):
    name				= "Blacklist"
    requestAutoload		= False
    version				= "1.0"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    author				= "Luemmel"
    description			= "Blacklist nicknames."
    offersConfigure		= True
    commandKeyword		= ""
    infoTitle			= None
    hotkeys				= []
    directory			= path.join(getPluginPath(), "pyTSon", "scripts", "blacklist")
    bl 					= []
    gomme_uid          	= "QTRtPmYiSKpMS8Oyd4hyztcvLqU="
    dlg = None

    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Add nickname to blacklist", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 1, "Remove nickname form blacklist", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Blacklist settings", "")]

    def __init__(self):
        # Database connect
        self.db = QSqlDatabase.addDatabase("QSQLITE", "pyTSon_blacklist")
        self.db.setDatabaseName(path.join(self.directory, "blacklist.db"))
        if not self.db.isValid():
            raise Exception("Database invalid")
        if not self.db.open():
            raise Exception("Could not open database.")

        s = self.db.exec_("SELECT * FROM settings")
        if s.next():
            self.active = bool(s.value("active"))
            self.ignore = bool(s.value("ignore"))

        d = self.db.exec_("SELECT * FROM blacklist ORDER BY name ASC")
        while d.next():
            self.bl.append(str(d.value("name")))

    def stop(self):
        self.db.close()
        self.db.delete()
        QSqlDatabase.removeDatabase("pyTSon_blacklist")

    def configure(self, qParentWidget):
        self.open_dlg()

    def bl_txt_update(self):
        with open(self.txt, 'wb') as fp:pickle.dump(self.bl, fp)

    def bl_add(self, nickname):
        nickname_low = nickname.lower()
        if nickname_low not in self.bl:
            self.db.exec_("INSERT INTO blacklist (name) VALUES ('"+nickname_low+"')")
            self.bl.append(nickname_low)
            self.bl.sort()
            ts3lib.printMessageToCurrentTab("\""+nickname+"\" is [b]now[/b] blacklisted.")
        else:ts3lib.printMessageToCurrentTab("\""+nickname+"\" is [b]already[/b] blacklisted.")

    def bl_remove(self, nickname):
        self.db.exec_("DELETE FROM blacklist WHERE name = '"+nickname+"'")
        self.bl.remove(nickname)
        ts3lib.printMessageToCurrentTab("\""+nickname+"\" is [b]no longer[/b] blacklisted.")

    def open_dlg(self):
        if not self.dlg:
            self.dlg = SettingsDialog(self)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
        return True

    def onMenuItemEvent(self, sch_id, a_type, menu_item_id, selected_item_id):
        if a_type == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            (error, nickname) = ts3lib.getClientVariableAsString(sch_id, selected_item_id, ts3defines.ClientProperties.CLIENT_NICKNAME)
            if menu_item_id == 0:self.bl_add(nickname)
            if menu_item_id == 1:self.bl_remove(nickname)
        elif a_type == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menu_item_id == 0: self.open_dlg()

    def onClientMoveEvent(self, sch_id, user_id, old_channel_id, new_channel_id, visibility, move_message):
        if self.active:
            (error, cl_id) = ts3lib.getClientID(sch_id)
            (error, cl_ch) = ts3lib.getChannelOfClient(sch_id, cl_id)

            if new_channel_id == cl_ch and not user_id == cl_id:
                (error, nickname) = ts3lib.getClientVariableAsString(sch_id, user_id, ts3defines.ClientProperties.CLIENT_NICKNAME)
                nickname = nickname.lower()
                if self.ignore:
                    nickname = re.sub(r"\s+", '', nickname)
                for nick in self.bl:
                    if nick in nickname:
                        (error, suid) = ts3lib.getServerVariableAsString(sch_id, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
                        if suid == self.gomme_uid:
                            (error, dbid) = ts3lib.getClientVariableAsUInt64(sch_id, user_id, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                            ts3lib.requestSetClientChannelGroup(sch_id, [12], [cl_ch], [dbid])
                        else:
                            ts3lib.requestClientKickFromChannel(sch_id, user_id, "")

class SettingsDialog(QDialog):
    def __init__(self, blacklist, parent=None):
        self.bl = blacklist
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(pytson.getPluginPath(), "scripts", "blacklist", "blacklist.ui"))
        self.setWindowTitle("Blacklist by Luemmel")

        self.btn_add.clicked.connect(self.add)
        self.btn_remove.clicked.connect(self.remove)

        self.cb_active.toggled.connect(self.onoff)
        self.cb_ignore.toggled.connect(self.ignore)

        self.list.addItems(blacklist.bl)

        self.cb_active.setChecked(blacklist.active)
        self.cb_ignore.setChecked(blacklist.ignore)

    def add(self):
        text = self.input_text.toPlainText()
        self.bl.bl_add(text)
        self.list.clear()
        self.list.addItems(self.bl.bl)

    def remove(self):
        selected_item = self.list.currentItem().text()
        self.bl.bl_remove(selected_item)
        self.list.clear()
        self.list.addItems(self.bl.bl)

    def onoff(self):
        self.bl.active = self.cb_active.isChecked()
        self.bl.db.exec_("UPDATE settings SET ""active = "+str(int(self.bl.active)))
        if self.bl.active:
            ts3lib.printMessageToCurrentTab("Blacklist [b]enabled[/b].")
        else:
            ts3lib.printMessageToCurrentTab("Blacklist [b]disabled[/b].")

    def ignore(self):
        self.bl.ignore = self.cb_ignore.isChecked()
        self.bl.db.exec_("UPDATE settings SET ""ignore = "+str(int(self.bl.ignore)))
        if self.bl.ignore:
            ts3lib.printMessageToCurrentTab("Blacklist will [b]now[/b] ignore spaces.")
        else:
            ts3lib.printMessageToCurrentTab("Blacklist will [b]no longer[/b] ignore spaces.")
