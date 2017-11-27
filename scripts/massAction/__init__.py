from os import path
from datetime import datetime
from PythonQt.QtGui import QMessageBox, QInputDialog, QDialog, QLineEdit
from PythonQt.QtCore import Qt
from PythonQt.Qt import QApplication
from PythonQt import BoolResult
from ts3plugin import ts3plugin
from pytsonui import setupUi
from pluginhost import PluginHost
import ts3defines, ts3lib, pytson

class massAction(ts3plugin):
    name = "Mass Actions"

    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Gives you the ability to take actions to all users in a channel or the server."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    debug = False
    banned_names = ["BAN", "NOT WELCOME"]
    sbgroup = 0
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "== {0} ==".format(name), ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Message all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "OfflineMessage all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 3, "Message all Channels", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 4, "Poke all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 5, "ChannelKick all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 6, "ChannelBan all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 7, "Kick all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 8, "Ban all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 9, "Delete all Channels", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 10, "== {0} ==".format(name), ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 11, "== {0} ==".format(name), ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 1, "Message all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 2, "OfflineMessage all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 3, "Poke all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 4, "ChannelKick all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 5, "ChannelBan all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 6, "Kick all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 7, "Ban all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 8, "Give Talk Power", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 12, "== {0} ==".format(name), "")
    ]
    dlg = None
    ok = BoolResult()

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        self.requested = True;ts3lib.requestChannelGroupList(ts3lib.getCurrentServerConnectionHandlerID())
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def menuCreated(self):
        for id in [0,10,11,12]:
            ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, id), False)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        try:
            if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
                if menuItemID == 1: # Message all Clients
                    (error, clients) = ts3lib.getClientList(schid)
                    msgs = self.getText(multiline=True,title="Message all %s clients on this server"%len(clients),text="Enter Private Message")
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        for msg in msgs: ts3lib.requestSendPrivateTextMsg(schid, msg, c)
                elif menuItemID == 2: # OffineMessage all Clients
                    (error, clients) = ts3lib.getClientList(schid)
                    (error, ownID) = ts3lib.getClientID(schid)
                    uids = []
                    for c in clients:
                        if c == ownID: continue
                        (error, uid) = ts3lib.getClientVariableAsString(schid, c, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                        uids.append(uid)
                    if not self.dlg: self.dlg = MessageDialog(schid, uids)
                    self.dlg.show();self.dlg.raise_();self.dlg.activateWindow()
                elif menuItemID == 3: # Message all Channels
                    (error, channels) = ts3lib.getChannelList(schid)
                    msgs = self.getText(multiline=True,title="Message all %s channels on this server"%len(channels),text="Enter Channel Message")
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in channels:
                        error = ts3lib.requestClientMove(schid, ownID, c, "123")
                        if not error == ts3defines.ERROR_ok: continue
                        for msg in msgs: ts3lib.requestSendChannelTextMsg(schid, msg, c)
                elif menuItemID == 4: # Poke all Clients
                    (error, clients) = ts3lib.getClientList(schid)
                    msgs = self.getText(title="Poke all %s clients on this server"%len(clients),text="Enter Poke Message",max=100)
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        for msg in msgs: ts3lib.requestClientPoke(schid, c, msg)
                elif menuItemID == 5: # ChannelKick all Clients
                    (error, clients) = ts3lib.getClientList(schid)
                    msg = self.getText(title="Kick all %s clients on this server from their channel"%len(clients),text="Enter Kick Reason",multimsg=False,max=80)
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.requestClientKickFromChannel(schid, c, msg)
                elif menuItemID == 6: # ChannelBan all Clients
                    (error, clients) = ts3lib.getClientList(schid)
                    msg = self.getText(title="ChannelBan all %s clients on this server"%len(clients),text="Enter Kick Reason",multimsg=False,max=80)
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        (error, chan) = ts3lib.getChannelOfClient(schid, selectedItemID)
                        (error, dbid) = ts3lib.getClientVariableAsUInt64(schid, c, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                        ts3lib.requestSetClientChannelGroup(schid, [self.sbgroup], [chan], [dbid])
                        ts3lib.requestClientKickFromChannel(schid, c, msg)
                elif menuItemID == 7: # Kick all Clients
                    (error, clients) = ts3lib.getClientList(schid)
                    msg = self.getText(title="Kick all %s clients from this server"%len(clients),text="Enter Kick Reason",multimsg=False,max=80)
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.requestClientKickFromServer(schid, c, msg)
                elif menuItemID == 8: # Ban all Clients
                    (error, clients) = ts3lib.getClientList(schid)
                    msg = self.getText(title="Ban all %s clients from this server"%len(clients),text="Enter Ban Reason",multimsg=False,max=80)
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.banclient(schid, c, -1, msg)
                elif menuItemID == 9: # Delete all Channels
                    (error, channels) = ts3lib.getChannelList(schid)
                    confirmation = self.confirm('Delete all Channels', 'Do you really want to delete all {0} channels on this server?'.format(len(channels)))
                    if not confirmation: return
                    for c in channels: ts3lib.requestChannelDelete(schid, c, True)
            elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL:
                if menuItemID == 1: # Message all Clients
                    (error, clients) = ts3lib.getChannelClientList(schid, selectedItemID)
                    (err, name) = ts3lib.getChannelVariableAsString(schid, selectedItemID, ts3defines.ChannelProperties.CHANNEL_NAME)
                    msgs = self.getText(multiline=True,title="Message to all %s clients in channel \"%s\""%(len(clients),name),text="Enter Private Message")
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        for msg in msgs: ts3lib.requestSendPrivateTextMsg(schid, msg, c)
                if menuItemID == 2: # OfflineMessage all Clients
                    (error, clients) = ts3lib.getChannelClientList(schid, selectedItemID)
                    (error, ownID) = ts3lib.getClientID(schid)
                    uids = []
                    for c in clients:
                        if c == ownID: continue
                        (error, uid) = ts3lib.getClientVariableAsString(schid, c, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                        uids.append(uid)
                    if not self.dlg: self.dlg = MessageDialog(schid, uids)
                    self.dlg.show();self.dlg.raise_();self.dlg.activateWindow()
                elif menuItemID == 3: # Poke all Clients
                    (error, clients) = ts3lib.getChannelClientList(schid, selectedItemID)
                    (err, name) = ts3lib.getChannelVariableAsString(schid, selectedItemID, ts3defines.ChannelProperties.CHANNEL_NAME)
                    msgs = self.getText(title="Poke all %s clients in channel \"%s\""%(len(clients),name),text="Enter Poke Message",max=100)
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        for msg in msgs: ts3lib.requestClientPoke(schid, c, msg)
                elif menuItemID == 4: # ChannelKick all Clients
                    (error, clients) = ts3lib.getChannelClientList(schid,selectedItemID)
                    (err, name) = ts3lib.getChannelVariableAsString(schid, selectedItemID, ts3defines.ChannelProperties.CHANNEL_NAME)
                    msg = self.getText(title="Kick all %s clients from channel \"%s\""%(len(clients),name),text="Enter Kick Reason",multimsg=False,max=80)
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.requestClientKickFromChannel(schid, c, msg)
                elif menuItemID == 5: # ChannelBan all Clients
                    (error, clients) = ts3lib.getChannelClientList(schid,selectedItemID)
                    (err, name) = ts3lib.getChannelVariableAsString(schid, selectedItemID, ts3defines.ChannelProperties.CHANNEL_NAME)
                    msg = self.getText(title="ChannelBan all %s clients from channel \"%s\""%(len(clients),name),text="Enter Kick Reason",multimsg=False,max=80)
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        (error, dbid) = ts3lib.getClientVariableAsUInt64(schid, c, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                        ts3lib.requestSetClientChannelGroup(schid, [self.sbgroup], [selectedItemID], [dbid])
                        ts3lib.requestClientKickFromChannel(schid, c, msg)
                elif menuItemID == 6: # Kick all Clients
                    (error, clients) = ts3lib.getChannelClientList(schid,selectedItemID)
                    (err, name) = ts3lib.getChannelVariableAsString(schid, selectedItemID, ts3defines.ChannelProperties.CHANNEL_NAME)
                    msg = self.getText(title="Kick all %s clients in channel \"%s\" from this server"%(len(clients),name),text="Enter Kick Reason",multimsg=False,max=80)
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.requestClientKickFromServer(schid, c, msg)
                elif menuItemID == 7: # Ban all Clients
                    (error, clients) = ts3lib.getChannelClientList(schid,selectedItemID)
                    (err, name) = ts3lib.getChannelVariableAsString(schid, selectedItemID, ts3defines.ChannelProperties.CHANNEL_NAME)
                    msg = self.getText(title="Ban all %s clients in channel \"%s\""%(len(clients),name),text="Enter Ban Reason",multimsg=False,max=80)
                    if bool(self.ok) != True:return
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.banclient(schid, c, -1, msg)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def getText(self,multimsg=True,multiline=False,title="Enter text here",text="",max=1024):
        try:
            x = QDialog()
            x.setAttribute(Qt.WA_DeleteOnClose)
            if multiline:
                clipboard = QApplication.clipboard().text()
                _message = QInputDialog.getMultiLineText(x, title, text, clipboard)
            else: _message = QInputDialog.getText(x, title, text, QLineEdit.Normal, "", self.ok)
            if multimsg: return [_message[i:i + max] for i in range(0, len(_message), max)]
            else: return _message[:max]
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def confirm(self, title, message):
        x = QDialog()
        x.setAttribute(Qt.WA_DeleteOnClose)
        _t = QMessageBox.question(x, title, message, QMessageBox.Yes, QMessageBox.No)
        if _t == QMessageBox.Yes: return True
        else: return False

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.requested = True;ts3lib.requestChannelGroupList(schid)

    def onChannelGroupListEvent(self, schid, channelGroupID, name, atype, iconID, saveDB):
        if self.requested:
            for _name in self.banned_names:
                if name.upper().__contains__(_name): self.sbgroup = channelGroupID;break

    def onChannelGroupListFinishedEvent(self, schid):
        if self.requested: self.requested = False

class MessageDialog(QDialog):
    def __init__(self, schid, uids, parent=None):
        try:
            self.schid = schid;self.uids = uids
            super(QDialog, self).__init__(parent)
            setupUi(self, path.join(pytson.getPluginPath(), "scripts", "onlineOfflineMessages", "message.ui"))
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Offline Message to {0} clients.".format(len(uids)))
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_send_clicked(self):
        for uid in self.uids:
            try: ts3lib.requestMessageAdd(self.schid, uid, self.subject.text, self.message.toPlainText())
            except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_cancel_clicked(self): self.close()
