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
    interval = 2000
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
        ts3lib.printMessageToCurrentTab('Timer restarted!')

    def tick(self):
        if self.debug: ts3lib.printMessageToCurrentTab('toggle: {0} | schid: {1} | count: {2} | interval: {3} | active: {4}'.format(self.toggle, self.schid, self.count, self.interval, self.active))
        if not self.active: return
        self.count += 1
        ts3lib.requestIsTalker(self.schid, False, "")
        ts3lib.requestIsTalker(self.schid, True, "Request #{}".format(self.count))

    def talker(self):
        (err, id) = ts3lib.getClientID(self.schid)
        (err, cid) = ts3lib.getChannelOfClient(self.schid, id)
        (err, ntp) = ts3lib.getChannelVariableAsInt(self.schid, cid, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        (err, talker) = ts3lib.getClientVariableAsInt(self.schid, id, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
        ret = True if talker or ntp < 1 else False
        if self.debug: ts3lib.printMessageToCurrentTab('talker() ret: {} | talker: {} | ntp: {} | cid: {} | id: {}'.format(ret, talker, ntp, cid, id))
        return ret

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
            if menuItemID == 0:
                self.toggle = 1
            elif menuItemID == 1:
                if self.active: self.toggle = 0;self.active = False
                else:
                    self.schid = schid;self.toggle = 2
                    if self.talker(): self.active = False
                    else: self.active = True
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.toggle))

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.toggle or schid != self.schid: return
        (error, ownid) = ts3lib.getClientID(schid)
        if ownid != clientID: return
        (error, ntp) = ts3lib.getChannelVariableAsInt(schid, newChannelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        (error, talker) = ts3lib.getClientVariableAsInt(schid, ownid, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
        if self.debug: ts3lib.printMessageToCurrentTab('onClientMoveEvent talker: {0} | ntp: {1}'.format(talker,ntp))
        if ntp < 1: return
        if self.toggle == 1 and not talker:
            self.nwmc = QNetworkAccessManager()
            self.nwmc.connect("finished(QNetworkReply*)", self.jokeReply)
            # self.schid = schid
            self.nwmc.get(QNetworkRequest(QUrl("http://tambal.azurewebsites.net/joke/random")))
        elif self.toggle == 2:
            if self.talker(): self.active = False
            else: self.active = True


    def onUpdateClientEvent(self, schid, clientID, invokerID, invokerName, invokerUniqueIdentifier):
        if not self.toggle or schid != self.schid: return
        (error, cID) = ts3lib.getClientID(self.schid)
        if not cID == clientID: return
        (error, ownid) = ts3lib.getClientID(schid)
        (error, talker) = ts3lib.getClientVariableAsInt(schid, ownid, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
        if self.debug: ts3lib.printMessageToCurrentTab('onUpdateClientEvent talker: {}'.format(talker))
        if self.talker(): self.active = False
        else: self.active = True

    def jokeReply(self, reply):
        if not self.toggle == 1: return
        joke = json.loads(reply.readAll().data().decode('utf-8'))["joke"]
        ts3lib.logMessage("Requesting talk power with joke\n%s"%joke, ts3defines.LogLevel.LogLevel_INFO, self.name, self.schid)
        if self.msg == "": msg =joke[:50]
        else: msg = self.msg
        if self.debug: ts3lib.printMessageToCurrentTab('[{0}] msg: {1}'.format(self.name,msg))
        ts3lib.requestIsTalker(self.schid, True, msg)