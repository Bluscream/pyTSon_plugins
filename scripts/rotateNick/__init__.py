import ts3defines, ts3lib, traceback, pytson, configparser
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtCore import QTimer, Qt
from PythonQt.QtGui import QMessageBox, QInputDialog, QWidget, QDialog
from pytsonui import setupUi
from os import path

def errorMsgBox(title, text):
    QMessageBox.critical(None, title, text)

def inputBox(title, text):
    x = QWidget()
    x.setAttribute(Qt.WA_DeleteOnClose)
    return QInputDialog.getText(x, title, text)

class rotateNick(ts3plugin):
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
    seperator = "꧂"
    schid = 0
    i = max-2
    b = 0
    dlg = None
    ini = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "rotateNick", "config.ini")
    config = configparser.ConfigParser()

    def separator(self, sep=None):
        if sep: self.config.set('general', 'separator', sep.replace(" ", "\s"))
        else: return self.config.get('general', 'separator').replace("\s", " ")

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if path.isfile(self.ini):
            self.config.read(self.ini)
        else:
            self.config["general"] = { "cfgver": "1", "debug": "False", "nick": "TeamspeakUser", "customNick": "False", "interval": "1000", "separator": " " }
            with open(self.ini, 'w') as configfile:
                self.config.write(configfile)

        # if self.timer is None:
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def stop(self): self.stopTimer()

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            if hasattr(self.timer, "isActive") and self.timer.isActive(): self.stopTimer()
            else:
                self.schid = schid
                if not self.dlg: self.dlg = dialog(self)
                self.dlg.show()
                self.dlg.raise_()
                self.dlg.activateWindow()

    def startTimer(self, interval=1000, nick=None):
        try:
            self.nick = nick
            # if len(nick) > self.max-2: errorMsgBox("Error", "Nickname must be %s chars or below!"%self.max); return
            self.i = self.max - 2
            self.b = 0
            # step = inputBox(self.name, 'Interval in Milliseconds:')
            # if step: interval = int(step)
            # else: interval = 300
            self.timer.start(interval)
            ts3lib.printMessageToCurrentTab('Timer started!')
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def stopTimer(self):
        if hasattr(self.timer, "isActive") and self.timer.isActive():
            self.timer.stop()
            # self.timer = None
            ts3lib.setClientSelfVariableAsString(self.schid, ts3defines.ClientProperties.CLIENT_NICKNAME, self._nick)
            ts3lib.flushClientSelfUpdates(self.schid)
            ts3lib.printMessageToCurrentTab('Timer stopped!')

    def tick(self):
        try:
            if self.schid == 0: return
            max = self.max - 1
            _nick = list(self.nick)
            if self.i == (len(_nick) * -1) + 2:
                self.i = max
                self.b = 0
            self.i -= 1
            self.b += 1
            # ts3lib.printMessageToCurrentTab("self.i == %s | self.b == %s"%(self.i,self.b))
            count = 0
            newnick = ["!"]

            for k in range(0, self.i):
                newnick.append(self.separator())
                count += 1

            if self.i > 1:
                for k in range(0, self.b):
                    if k < len(_nick) and k < max:
                        newnick.append(_nick[k])
                        # ts3lib.printMessageToCurrentTab("1: {} | 2: {} | 3: {}".format(0, self.b, self._nick[k]))
                        count += 1
                    else:
                        pass
                #for k in range(count, max):
                    #newnick.append(separator())
            else:
                for k in range(self.i * -1, len(_nick)):
                    if k != -1 and count < max:
                        newnick.append(_nick[k])
                        count += 1
                #for k in range(count, max):
                    #newnick.append(self.separator())
            # newnick.append("!")
            _newnick = ''.join(newnick)
            if _newnick is None: return
            # ts3lib.printMessageToCurrentTab("length: {} | newnick: \"{}\"".format(len(_newnick), _newnick))
            ts3lib.setClientSelfVariableAsString(self.schid, ts3defines.ClientProperties.CLIENT_NICKNAME, _newnick)
            ts3lib.flushClientSelfUpdates(self.schid)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

class dialog(QDialog):
    def __init__(self, rotateNick, parent=None):
        try:
            self.rotateNick = rotateNick
            super(QDialog, self).__init__(parent)
            setupUi(self, path.join(pytson.getPluginPath(), "scripts", rotateNick.__class__.__name__, "dialog.ui"))
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle(rotateNick.name)
            self.nick.setText(self.rotateNick.config.get('general', 'nick'))
            self.separator.setText(self.rotateNick.separator())
            customNick = self.rotateNick.config.get('general', 'customNick')
            self.customNick.setChecked(True if customNick == "True" else False)
            self.interval.value = int(self.rotateNick.config.get('general', 'interval'))
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_btn_start_clicked(self):
        try:
            if not self.rotateNick.timer.isActive():
                (err, _nick) = ts3lib.getClientSelfVariable(self.rotateNick.schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
                if self.customNick.checked:
                    nick = self.nick.text
                else:
                    nick = _nick
                self.rotateNick._nick = _nick
                self.rotateNick.separator(self.separator.text)
                # self.rotateNick.config.set('general', 'separator', self.separator.text)
                self.rotateNick.startTimer(self.interval.value, nick)
                self.btn_start.setText("Stop")
            else:
                self.rotateNick.stopTimer()
                self.btn_start.setText("Start")
            # elf.close()
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_btn_cancel_clicked(self):
        try:
            self.rotateNick.separator(self.separator.text)
            # self.rotateNick.config.set('general', 'separator', self.separator.text)
            self.rotateNick.config.set('general', 'nick', self.nick.text)
            self.rotateNick.config.set('general', 'customNick', str(self.customNick.checked))
            self.rotateNick.config.set('general', 'interval', str(self.interval.value))
            with open(self.rotateNick.ini, 'w') as configfile:
                self.rotateNick.config.write(configfile)
            self.close()
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
