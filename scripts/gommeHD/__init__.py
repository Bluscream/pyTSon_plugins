import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin
from datetime import datetime

class gommeHD(ts3plugin):
    name = "GommeHD nifty tricks"
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
    msg = "um nur Personen ab dem ausgewählen Rang die Möglichkeit zu geben, in deinen Channel zu joinen."

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if fromUniqueIdentifier != "serveradmin": return
        if fromName != "Gomme-Bot": return
        if not message.endswith(self.msg): return
        ts3lib.requestSendPrivateTextMsg(schid, "registriert", fromID)