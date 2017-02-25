import ts3lib, ts3defines
from ts3plugin import ts3plugin
from datetime import datetime
from PythonQt.QtGui import QInputDialog, QWidget, QMessageBox

class joinChannel(ts3plugin):
    name = "Channel Queue"
    apiVersion = 21
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

    def __init__(self):
        ts3lib.logMessage(self.name + " script for pyTSon by " + self.author + " loaded from \"" + __file__ + "\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format( datetime.now()) + " [color=orange]" + self.name + "[/color] Plugin for pyTSon by [url=https://github.com/" + self.author + "]" + self.author + "[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, channel):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL and menuItemID == 0:
            x = QWidget()
            password = QInputDialog.getText(x, "Enter Channel Password", "Password:")
            (error, clients) = ts3lib.getChannelVariableAsInt(schid, channel, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
            (error, maxclients) = ts3lib.getChannelVariableAsInt(schid, channel, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
            (error, maxfamilyclients) = ts3lib.getChannelVariableAsInt(schid, channel, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
            if clients < maxclients and clients < maxfamilyclients:
                (error, ownID) = ts3lib.getClientID(schid)
                ts3lib.requestClientMove(schid,ownID,channel,password)
                return True
            self.schid = schid;self.channel = channel;self.password = password
            (error, name) = ts3lib.getChannelVariableAsString(schid, channel, ts3defines.ChannelProperties.CHANNEL_NAME)
            ts3lib.printMessageToCurrentTab("Queued for channel \"{0}\" [color=red]{1}[/color] clients remaining.".format(name, maxclients-clients+1))

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if self.schid == schid and self.channel == oldChannelID:
            (error, clients) = ts3lib.getChannelVariableAsInt(schid, self.channel, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
            (error, maxclients) = ts3lib.getChannelVariableAsInt(schid, self.channel, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
            (error, maxfamilyclients) = ts3lib.getChannelVariableAsInt(schid, self.channel, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
            if clients < maxclients and clients < maxfamilyclients:
                (error, ownID) = ts3lib.getClientID(schid)
                ts3lib.requestClientMove(schid,ownID,self.channel,self.password)
                self.schid = 0; self.channel = 0; self.password = ""
                
    def onDelChannelEvent(self, schid, channel, invokerID, invokerName, invokerUniqueIdentiﬁer):
        if self.schid == schid and self.channel == channel:
            self.schid = 0;self.channel = 0
            (error, name) = ts3lib.getChannelVariableAsString(schid, channel, ts3defines.ChannelProperties.CHANNEL_NAME)
            msgBox = QMessageBox()
            msgBox.setText("Channel \"{0}\" got deleted by \"{1}\"\n\nStopping Queue!".format(name, invokerName))
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.exec()