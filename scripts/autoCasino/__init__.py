import pytson, ts3lib, ts3defines
from random import randint
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtCore import QTimer
from collections import defaultdict

class autoCasino(ts3plugin):
    name = "Auto Casino"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = False
    sUID = "qdIe8FnQrSTpYhfAlaqaVp8OEGQ="
    botNick = "PhynixGaming.NET Casino"
    botUID = "EkfzBP4YlKCsWwVKhI8fIM2VNck="
    msg = "Das Spiel wurde gestartet jeder der mitspielen möchte schreibt !play"
    bet = 11
    delay = 500
    schid = 0
    botCLID = 0

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if targetMode != ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL: return
        if fromUniqueIdentifier != self.botUID: return
        if fromName != self.botNick: return
        (err, suid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if suid != self.sUID: return
        if message != self.msg: return
        ts3lib.requestSendChannelTextMsg(schid, "!play", toID)
        self.schid = schid; self.botCLID = fromID;
        QTimer.singleShot(self.delay, self.bet)

    def bet(self):
        ts3lib.requestSendPrivateTextMsg(self.schid, "!pay 11", self.botCLID)
        ts3lib.requestSendPrivateTextMsg(self.schid, "!set {0}".format(randint(1, 100)), self.botCLID)