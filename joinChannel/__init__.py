import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtGui import QInputDialog, QWidget, QMessageBox
from PythonQt.QtCore import Qt

class joinChannel(ts3plugin):
    name = "Channel Queue"
    apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Let's you join a channel instantly after enough slots have been free'd."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Queue", "")]
    hotkeys = []
    debug = False
    schid = 0
    channel = 0
    password = ""
    cname = ""

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, channel):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL and menuItemID == 0:
            try:
                x = QWidget()
                x.setAttribute(Qt.WA_DeleteOnClose)
                password = QInputDialog.getText(x, "Enter Channel Password", "Password:")
                clients = self.channelClientCount(schid, channel)
                if self.debug: ts3lib.printMessageToCurrentTab("clients: {0}".format(clients))
                (error, maxclients) = ts3lib.getChannelVariableAsUInt64(schid, channel, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
                if self.debug: ts3lib.printMessageToCurrentTab("error: {0} | maxclients: {1}".format(error,maxclients))
                (error, maxfamilyclients) = ts3lib.getChannelVariableAsUInt64(schid, channel, ts3defines.ChannelProperties.CHANNEL_MAXFAMILYCLIENTS)
                if self.debug: ts3lib.printMessageToCurrentTab("error: {0} | maxfamilyclients: {1}".format(error,maxfamilyclients))
                if clients < maxclients and clients < maxfamilyclients:
                    (error, ownID) = ts3lib.getClientID(schid)
                    ts3lib.requestClientMove(schid,ownID,channel,password)
                    return True
                (error, name) = ts3lib.getChannelVariableAsString(schid, channel, ts3defines.ChannelProperties.CHANNEL_NAME)
                self.schid = schid;self.channel = channel;self.password = password;self.cname = name
                if password == "": ts3lib.printMessageToCurrentTab("Queued for channel [url=channelid://{0}]{1}[/url]. [color=red]{2}[/color] client(s) remaining.".format(channel, name, maxclients-clients+1))
                else: ts3lib.printMessageToCurrentTab("Queued for channel [url=channelid://{0}]{1}[/url] with password \"{2}\". [color=red]{3}[/color] client(s) remaining.".format(channel, name, password, maxclients-clients+1))
            except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if self.schid == schid and self.channel == oldChannelID:
            clients = self.channelClientCount(schid, oldChannelID)
            if self.debug: ts3lib.printMessageToCurrentTab("clients: {0}".format(clients))
            (error, maxclients) = ts3lib.getChannelVariableAsUInt64(schid, oldChannelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
            if self.debug: ts3lib.printMessageToCurrentTab("error: {0} | maxclients: {1}".format(error,maxclients))
            (error, maxfamilyclients) = ts3lib.getChannelVariableAsUInt64(schid, oldChannelID, ts3defines.ChannelProperties.CHANNEL_MAXFAMILYCLIENTS)
            if self.debug: ts3lib.printMessageToCurrentTab("error: {0} | maxfamilyclients: {1}".format(error,maxfamilyclients))
            if clients < maxclients and clients < maxfamilyclients:
                (error, ownID) = ts3lib.getClientID(schid)
                ts3lib.requestClientMove(schid,ownID,oldChannelID,self.password)
                self.schid = 0; self.channel = 0; self.password = "";self.name = ""
            else: ts3lib.printMessageToCurrentTab("{0} left channel [url=channelid://{1}]{2}[/url]. [color=red]{3}[/color] client(s) remaining.".format(self.clientURL(schid, clientID),channel, name, maxclients-clients+1))

    def onUpdateChannelEditedEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentiﬁer):
        if self.debug: ts3lib.printMessageToCurrentTab("self.schid: {0} | schid: {1}".format(self.schid,schid))
        if self.debug: ts3lib.printMessageToCurrentTab("self.channel: {0} | channelID: {1}".format(self.channel,channelID))
        if self.schid == schid and self.channel == channelID:
            clients = self.channelClientCount(schid, channelID)
            if self.debug: ts3lib.printMessageToCurrentTab("clients: {0}".format(clients))
            (error, maxclients) = ts3lib.getChannelVariableAsUInt64(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
            if self.debug: ts3lib.printMessageToCurrentTab("error: {0} | maxclients: {1}".format(error,maxclients))
            (error, maxfamilyclients) = ts3lib.getChannelVariableAsUInt64(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXFAMILYCLIENTS)
            if self.debug: ts3lib.printMessageToCurrentTab("error: {0} | maxfamilyclients: {1}".format(error,maxfamilyclients))
            if clients < maxclients and clients < maxfamilyclients:
                (error, ownID) = ts3lib.getClientID(schid)
                ts3lib.requestClientMove(schid,ownID,channelID,self.password)
                self.schid = 0; self.channel = 0; self.password = "";self.name = ""

    def onDelChannelEvent(self, schid, channel, invokerID, invokerName, invokerUniqueIdentiﬁer):
        if self.schid == schid and self.channel == channel:
            msgBox = QMessageBox()
            msgBox.setText("Channel \"{0}\" got deleted by \"{1}\"\n\nStopping Queue!".format(self.cname, invokerName))
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.exec()
            self.schid = 0;self.channel = 0;self.password = "";self.name = ""

    def channelClientCount(self, schid, channelID):
            (error, clients) = ts3lib.getChannelClientList(schid, channelID)
            if error == ts3defines.ERROR_ok: return len(clients)
            else: return error

    def clientURL(self, schid=None, clid=1, uid=None, nickname=None, encodednick=None):
        if schid == None:
            try: schid = ts3lib.getCurrentServerConnectionHandlerID()
            except: pass
        if uid == None:
            try: (error, uid) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            except: pass
        if nickname == None:
            try: (error, nickname) = ts3lib.getClientDisplayName(schid, clid)
            except: nickname = uid
        if encodednick == None:
            try: encodednick = urlencode(nickname)
            except: pass
        return "[url=client://%s/%s~%s]%s[/url]" % (clid, uid, encodednick, nickname)
