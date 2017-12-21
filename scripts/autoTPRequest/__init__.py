import ts3defines, ts3lib, json
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PythonQt.QtCore import QUrl, Qt, QTimer
from PythonQt.QtGui import QInputDialog, QWidget
from urllib.parse import quote_plus as urlencode
from ts3plugin import ts3plugin
from datetime import datetime

def inputBox(title, text):
    x = QWidget()
    x.setAttribute(Qt.WA_DeleteOnClose)
    return QInputDialog.getText(x, title, text)

class autoTPRequest(ts3plugin):
    name = "Auto Talk Power Request"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Automatically request talk power when switching channels.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Auto Talk Power", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Toggle Talk Power Spam", "")]
    hotkeys = []
    debug = True
    msg = ""
    toggle = 0
    timer = QTimer()
    schid = 0
    count = 0
    interval = 5000
    active = False

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        try:
            self.timer.timeout.connect(self.tick)
            self.schid = ts3lib.getCurrentServerConnectionHandlerID()
            self.timer.start(self.interval)
            if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def stop(self):
        self.timer.stop()
        self.schid = 0
        self.count = 0
        self.toggle = 0
        ts3lib.printMessageToCurrentTab('Timer stopped!')

    def stopTimer(self):
        try:
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def startTimer(self):
        try:

            ts3lib.printMessageToCurrentTab('Timer started!')
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def toggleTimer(self, schid=None):
        try:
            if hasattr(self.timer, "isActive") and self.timer.isActive(): self.stopTimer()
            else: self.startTimer(schid)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def tick(self):
        try:
            if not self.active: return
            self.count += 1
            ts3lib.requestIsTalker(self.schid, False, "")
            ts3lib.requestIsTalker(self.schid, True, "Request #{}".format(self.count))
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        try:
            if menuItemID == 0:
                self.toggle = 1
                ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.toggle))
            elif menuItemID == 1:
                self.toggle == 2
                (err, talker) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
                if not talker: self.startTimer(schid)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        try:
            if self.toggle == 0: return
            (error, ownid) = ts3lib.getClientID(schid)
            if ownid != clientID: return
            (error, ntp) = ts3lib.getChannelVariableAsInt(schid, newChannelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
            if self.debug: ts3lib.printMessageToCurrentTab('error: {0} | ntp: {1}'.format(error,ntp))
            if ntp < 1: return
            (error, talker) = ts3lib.getClientVariableAsInt(schid, ownid, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
            if self.debug: ts3lib.printMessageToCurrentTab('error: {0} | talker: {1}'.format(error,talker))
            if talker: return
            if self.toggle == 1:
                self.nwmc = QNetworkAccessManager()
                self.nwmc.connect("finished(QNetworkReply*)", self.jokeReply)
                self.schid = schid
                self.nwmc.get(QNetworkRequest(QUrl("http://tambal.azurewebsites.net/joke/random")))
            elif self.toggle == 2: self.active = True
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)


    def onUpdateClientEvent(self, serverConnectionHandlerID, clientID, invokerID, invokerName, invokerUniqueIdentifier):
        try:
            if self.toggle == 0: return
            (error, cID) = ts3lib.getClientID(self.schid)
            if not cID == clientID: return
            (err, talker) = ts3lib.getClientSelfVariable(self.schid, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
            if talker: self.active = False
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def jokeReply(self, reply):
        if not self.toggle == 1: return
        joke = json.loads(reply.readAll().data().decode('utf-8'))["joke"]
        ts3lib.logMessage("Requesting talk power with joke\n%s"%joke, ts3defines.LogLevel.LogLevel_INFO, self.name, self.schid)
        if self.msg == "": msg =joke[:50]
        else: msg = self.msg
        if self.debug: ts3lib.printMessageToCurrentTab('[{0}] msg: {1}'.format(self.name,msg))
        try: ts3lib.requestIsTalker(self.schid, True, msg)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
