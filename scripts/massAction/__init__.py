from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtGui import QInputDialog, QWidget
from PythonQt.QtCore import Qt
from PythonQt.Qt import QApplication
from ts3client import IconPack
import ts3defines, ts3lib

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
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "Message all Channels", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 3, "Poke all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 4, "ChannelKick all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 5, "ChannelBan all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 6, "Kick all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 7, "Ban all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 8, "== {0} ==".format(name), ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "== {0} ==".format(name), ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 1, "Message all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 2, "Poke all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 3, "ChannelKick all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 4, "ChannelBan all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 5, "Kick all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 6, "Ban all Clients", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 7, "Give Talk Power", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 8, "== {0} ==".format(name), "")
    ]

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        self.requested = True;ts3lib.requestChannelGroupList(ts3lib.getCurrentServerConnectionHandlerID())
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        try:
            if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
                if menuItemID == 1: # Message all Clients
                    msgs = self.getText(multiline=True,title="Enter Private Message")
                    (error, clients) = ts3lib.getClientList(schid)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        for msg in msgs: ts3lib.requestSendPrivateTextMsg(schid, msg, c)
                elif menuItemID == 2: # Message all Channels
                    msgs = self.getText(multiline=True,title="Enter Channel Message")
                    (error, channels) = ts3lib.getChannelList(schid)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in channels:
                        error = ts3lib.requestClientMove(schid, ownID, c, "123")
                        if not error == ts3defines.ERROR_ok: continue
                        for msg in msgs: ts3lib.requestSendChannelTextMsg(schid, msg, c)
                elif menuItemID == 3: # Poke all Clients
                    msgs = self.getText(title="Enter Poke Message",max=100)
                    (error, clients) = ts3lib.getClientList(schid)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        for msg in msgs: ts3lib.requestClientPoke(schid, c, msg)
                elif menuItemID == 4: # ChannelKick all Clients
                    msg = self.getText(title="Enter Kick Reason",multimsg=False,max=80)
                    (error, clients) = ts3lib.getClientList(schid)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.requestClientKickFromChannel(schid, c, msg)
                elif menuItemID == 5: # ChannelBan all Clients
                    msg = self.getText(title="Enter Kick Reason",multimsg=False,max=80)
                    (error, clients) = ts3lib.getClientList(schid)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        (error, chan) = ts3lib.getChannelOfClient(schid, selectedItemID)
                        (error, dbid) = ts3lib.getClientVariableAsUInt64(schid, c, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                        ts3lib.requestSetClientChannelGroup(schid, [self.sbgroup], [chan], [dbid])
                        ts3lib.requestClientKickFromChannel(schid, c, msg)
                elif menuItemID == 6: # Kick all Clients
                    msg = self.getText(title="Enter Kick Reason",multimsg=False,max=80)
                    (error, clients) = ts3lib.getClientList(schid)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.requestClientKickFromServer(schid, c, msg)
                elif menuItemID == 7: # Ban all Clients
                    msg = self.getText(title="Enter Ban Reason",multimsg=False,max=80)
                    (error, clients) = ts3lib.getClientList(schid)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.banclient(schid, c, -1, msg)
            elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL:
                if menuItemID == 1: # Message all Clients
                    msgs = self.getText(multiline=True,title="Enter Private Message")
                    (error, clients) = ts3lib.getChannelClientList(schid, selectedItemID)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        for msg in msgs: ts3lib.requestSendPrivateTextMsg(schid, msg, c)
                elif menuItemID == 2: # Poke all Clients
                    msgs = self.getText(title="Enter Poke Message",max=100)
                    (error, clients) = ts3lib.getChannelClientList(schid, selectedItemID)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        for msg in msgs: ts3lib.requestClientPoke(schid, c, msg)
                elif menuItemID == 3: # ChannelKick all Clients
                    msg = self.getText(title="Enter Kick Reason",multimsg=False,max=80)
                    (error, clients) = ts3lib.getChannelClientList(schid,selectedItemID)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.requestClientKickFromChannel(schid, c, msg)
                elif menuItemID == 4: # ChannelBan all Clients
                    msg = self.getText(title="Enter Kick Reason",multimsg=False,max=80)
                    (error, clients) = ts3lib.getChannelClientList(schid,selectedItemID)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        (error, dbid) = ts3lib.getClientVariableAsUInt64(schid, c, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
                        ts3lib.requestSetClientChannelGroup(schid, [self.sbgroup], [selectedItemID], [dbid])
                        ts3lib.requestClientKickFromChannel(schid, c, msg)
                elif menuItemID == 5: # Kick all Clients
                    msg = self.getText(title="Enter Kick Reason",multimsg=False,max=80)
                    (error, clients) = ts3lib.getChannelClientList(schid,selectedItemID)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.requestClientKickFromServer(schid, c, msg)
                elif menuItemID == 6: # Ban all Clients
                    msg = self.getText(title="Enter Ban Reason",multimsg=False,max=80)
                    (error, clients) = ts3lib.getChannelClientList(schid,selectedItemID)
                    (error, ownID) = ts3lib.getClientID(schid)
                    for c in clients:
                        if c == ownID: continue
                        ts3lib.banclient(schid, c, -1, msg)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def getText(self,multimsg=True,multiline=False,title="Enter text here",text="",max=1024):
        try:
            x = QWidget()
            x.setAttribute(Qt.WA_DeleteOnClose)
            if multiline:
                clipboard = QApplication.clipboard().text();
                _message = QInputDialog.getMultiLineText(x, title, text, clipboard)
            else: _message = QInputDialog.getText(x, title, text)
            if multimsg: return [_message[i:i + max] for i in range(0, len(_message), max)]
            else: return _message[:max]
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.requested = True;ts3lib.requestChannelGroupList(schid)

    def onChannelGroupListEvent(self, schid, channelGroupID, name, atype, iconID, saveDB):
        if self.requested:
            for _name in self.banned_names:
                if name.upper().__contains__(_name): self.sbgroup = channelGroupID;break

    def onChannelGroupListFinishedEvent(self, schid):
        if self.requested: self.requested = False
