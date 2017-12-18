import ts3defines, ts3lib, traceback
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtCore import QTimer, Qt
from PythonQt.QtGui import QMessageBox, QInputDialog, QWidget

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
    max = ts3defines.TS3_MAX_SIZE_CLIENT_NICKNAME_NONSDK-2
    nick = "TeamspeakUser"
    _nick = []
    schid = 0
    i = max
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
                self.schid = 0;self.i = 30;self.b = 0;
                ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, self.nick)
                ts3lib.flushClientSelfUpdates(schid)
                ts3lib.printMessageToCurrentTab('Timer stopped!')
            else:
                (err, nick) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
                if len(nick) > self.max: errorMsgBox("Error", "Nickname must be %s chars or below!"%self.max); return
                self.nick = nick
                self._nick = list(nick)
                self.schid = schid
                step = inputBox(self.name, 'Interval in Milliseconds:')
                if step: interval = int(step)
                else: interval = 1000
                self.timer.start(interval)
                ts3lib.printMessageToCurrentTab('Timer started!')

    def tick(self):
        if self.schid == 0: return
        _newnick = self.fillnick()
        ts3lib.printMessageToCurrentTab("newnick: {}".format(_newnick))
        ts3lib.setClientSelfVariableAsString(self.schid, ts3defines.ClientProperties.CLIENT_NICKNAME, _newnick)
        ts3lib.flushClientSelfUpdates(self.schid)

    def fillnick(self):
        try:
            self.i -= 1
            self.b += 1
            ts3lib.printMessageToCurrentTab("self.i == %s | self.b == %s"%(self.i,self.b))
            newnick = ["!"]

            for k in range(0, self.i):
                newnick.append(" ")
                # ts3lib.printMessageToCurrentTab("test")

            if self.i >= 0 :
                for k in range(0,self.b):
                    if len(self._nick) < self.b:
                        #k anpassen das nicht über _nick len
                    newnick.append(self._nick[k])#((k+1)-self.max) * -1])
                    ts3lib.printMessageToCurrentTab("1: {} | 2: {} | 3: {}".format(0, self.b, self._nick[k]))
            return ''.join(newnick)
        except: ts3lib.printMessageToCurrentTab("[color=red]%s"%traceback.format_exc())