import ts3defines, ts3lib, traceback
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtCore import QTimer, Qt
from PythonQt.QtGui import QMessageBox, QInputDialog, QWidget,QDialog
from pytsonui import setupUi

def errorMsgBox(title, text):
    QMessageBox.critical(None, title, text)

def inputBox(title, text):
    x = QWidget()
    x.setAttribute(Qt.WA_DeleteOnClose)
    return QInputDialog.getText(x, title, text)

class countNick(ts3plugin):
    name = "Rotate Nickname"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Converts your nickname into an ugly marquee\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle rotating nickname", "")]
    hotkeys = []
    timer = None
    debug = False
    max = ts3defines.TS3_MAX_SIZE_CLIENT_NICKNAME_NONSDK
    nick = "TeamspeakUser"
    seperator = " "
    _nick = []
    schid = 0
    i = max-2
    b = 0
    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            if self.timer is None:
                self.timer = QTimer()
                self.timer.timeout.connect(self.tick)
            if self.timer.isActive():
                self.timer.stop()
                self.timer = None
                ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, self.nick)
                ts3lib.flushClientSelfUpdates(schid)
                ts3lib.printMessageToCurrentTab('Timer stopped!')
            else:
                (err, nick) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
                if len(nick) > self.max-2: errorMsgBox("Error", "Nickname must be %s chars or below!"%self.max); return
                self.nick = nick
                self._nick = list(nick)
                self.i = self.max - 2
                self.b = 0
                self.schid = schid
                step = inputBox(self.name, 'Interval in Milliseconds:')
                if step: interval = int(step)
                else: interval = 300
                self.timer.start(interval)
                ts3lib.printMessageToCurrentTab('Timer started!')

    def tick(self):
        if self.schid == 0: return
        _newnick = self.fillnick()
        if _newnick is None: return
        ts3lib.printMessageToCurrentTab("length: {} | newnick: \"{}\"".format(len(_newnick), _newnick))
        ts3lib.setClientSelfVariableAsString(self.schid, ts3defines.ClientProperties.CLIENT_NICKNAME, _newnick)
        ts3lib.flushClientSelfUpdates(self.schid)

    def fillnick(self):
            max = self.max - 2
            if self.i == (len(self._nick) * -1):
               self.i = max
               self.b = 0
            self.i -= 1
            self.b += 1
            #ts3lib.printMessageToCurrentTab("self.i == %s | self.b == %s"%(self.i,self.b))
            count = 0
            newnick = ["!"]

            for k in range(0, self.i):
                newnick.append(self.seperator)
                count += 1

            if self.i > 1 :
                for k in range(0,self.b):
                    if  k < len(self._nick) and k < max:
                        newnick.append(self._nick[k])
                        #ts3lib.printMessageToCurrentTab("1: {} | 2: {} | 3: {}".format(0, self.b, self._nick[k]))
                        count += 1
                    else:
                        pass
                for k in range(count, max):
                    newnick.append(self.seperator)
            else:
                 for k in range(self.i * -1 ,len(self._nick)):
                      if k != -1 and count < max:
                          newnick.append(self._nick[k])
                          count +=1
                 for k in range(count, max):
                      newnick.append(self.seperator)
            newnick.append("!")
            return ''.join(newnick)

class MessageDialog(QDialog):
    def __init__(self, countNick, parent=None):
        try:
            self.countNick = countNick
            super(QDialog, self).__init__(parent)
            setupUi(self, path.join(pytson.getPluginPath(), "scripts", countNick.__name__, "dialog.ui"))
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle(countNick.Name)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_btn_apply_clicked(self):
        for uid in self.uids:
            try: ts3lib.requestMessageAdd(self.schid, uid, self.subject.text, self.message.toPlainText())
            except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_cancel_clicked(self): self.close()
