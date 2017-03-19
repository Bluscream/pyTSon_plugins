import ts3defines, ts3lib, json
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PythonQt.QtCore import QUrl
from urllib.parse import quote_plus as urlencode
from ts3plugin import ts3plugin
from datetime import datetime

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
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Auto Talk Power", "")]
    hotkeys = []
    debug = False
    msg = ""
    toggle = True
    schid = 0

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.toggle = not self.toggle
            ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=yellow]{2}[/color]".format(self.timestamp(),self.name,self.toggle))

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if not self.toggle: return
        try:
            (error, ownid) = ts3lib.getClientID(schid)
            if ownid == clientID:
                (error, ntp) = ts3lib.getChannelVariableAsInt(schid, newChannelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
                if self.debug: ts3lib.printMessageToCurrentTab('error: {0} | ntp: {1}'.format(error,ntp))
                if ntp < 1: return
                (error, tp) = ts3lib.getClientVariableAsInt(schid, ownid, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
                if self.debug: ts3lib.printMessageToCurrentTab('error: {0} | tp: {1}'.format(error,tp))
                if tp: return
                self.nwmc = QNetworkAccessManager()
                self.nwmc.connect("finished(QNetworkReply*)", self.jokeReply)
                self.schid = schid
                self.nwmc.get(QNetworkRequest(QUrl("http://tambal.azurewebsites.net/joke/random")))
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def jokeReply(self, reply):
        if self.msg == "": msg =json.loads(reply.readAll().data().decode('utf-8'))["joke"][:50]
        else: msg = self.msg
        if self.debug: ts3lib.printMessageToCurrentTab('[{0}] msg: {1}'.format(self.name,msg))
        try: ts3lib.requestIsTalker(self.schid, True, msg);self.schid = 0
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
