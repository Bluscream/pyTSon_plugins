import ts3defines, ts3lib, re, pytson
from ts3plugin import ts3plugin
from datetime import datetime


class serverSwitcher(ts3plugin):
    name = 'Server Switcher'
    try:
        apiVersion = pytson.getCurrentApiVersion()
    except NameError:
        apiVersion = 22
    requestAutoload = False
    version = '1.0'
    author = 'Bluscream'
    description = 'Show others that you just switched to another tab.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins.'
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = True
    awaymsg = "Anderer TS"

    @staticmethod
    def timestamp():
        return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        ts3lib.logMessage('{0} script for pyTSon by {1} loaded from "{2}".'.format(self.name, self.author, __file__),
                          ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab(
            '{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.'.format(
                self.timestamp(), self.name, self.author))

    """
    def onIncomingClientQueryEvent(self, schid, commandText):
            command = commandText.split()
            if command[0] != 'notifyclientupdated': return
            clid = int(command[1].replace('clid=', ''))
            err, ownid = ts3lib.getClientID(schid)
            if clid != ownid: return
            var = command[2].split("=")
            if var[0] != 'client_input_hardware': return
            if var[1] != '1': return
            self.setStatus(schid, ownid)
    """

    def onClientSelfVariableUpdateEvent(self, schid, flag, oldValue, newValue):
        try:
            if flag == ts3defines.ClientProperties.CLIENT_INPUT_HARDWARE and newValue == "1":
                self.setStatus(schid)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0); pass

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        try:
            if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
                self.setStatus(schid)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0); pass

    def setStatus(self, schid):
        try:
            err, ownid = ts3lib.getClientID(schid)
            err, schids = ts3lib.getServerConnectionHandlerList()
            regex = re.compile(r'.*(<server>.*</server>).*', re.IGNORECASE)
            for tab in schids:
                err, meta_data = ts3lib.getClientSelfVariable(tab, ts3defines.ClientProperties.CLIENT_META_DATA)
                meta_data = regex.sub("", meta_data)
                if tab == schid:
                    ts3lib.setClientSelfVariableAsInt(tab, ts3defines.ClientPropertiesRare.CLIENT_AWAY,
                                                      ts3defines.AwayStatus.AWAY_NONE)
                else:
                    err, away = ts3lib.getClientSelfVariable(tab, ts3defines.ClientPropertiesRare.CLIENT_AWAY)
                    err, away_message = ts3lib.getClientSelfVariable(tab,
                                                                     ts3defines.ClientPropertiesRare.CLIENT_AWAY_MESSAGE)
                    if away == ts3defines.AwayStatus.AWAY_ZZZ and away_message == self.awaymsg: continue
                    ts3lib.setClientSelfVariableAsString(tab, ts3defines.ClientPropertiesRare.CLIENT_AWAY_MESSAGE,
                                                         self.awaymsg)
                    ts3lib.setClientSelfVariableAsInt(tab, ts3defines.ClientPropertiesRare.CLIENT_AWAY,
                                                      ts3defines.AwayStatus.AWAY_ZZZ)
                    err, ip = ts3lib.getConnectionVariableAsString(schid, ownid,
                                                                   ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
                    err, port = ts3lib.getConnectionVariableAsString(schid, ownid,
                                                                     ts3defines.ConnectionProperties.CONNECTION_SERVER_PORT)
                    # err, ip = ts3lib.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_IP)
                    # err, port = ts3lib.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_PORT)
                    meta_data = "{}<server>{}{}</server>".format(meta_data, ip, ":" + port if port else "")
                ts3lib.setClientSelfVariableAsString(tab, ts3defines.ClientProperties.CLIENT_META_DATA, meta_data)
                ts3lib.flushClientSelfUpdates(tab)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0); pass
