import ts3lib, ts3defines
from random import randint
from datetime import datetime
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from pytson import getCurrentApiVersion
from bluscream import timestamp, clientURL

class complaintReminder(ts3plugin):
    name = "Complaint Reminder"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Reminds you about due complaints."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    timer = QTimer()
    servers = {}
    waitingForList = []
    interval = 60*1000

    def __init__(self):
        self.timer.timeout.connect(self.tick)
        self.timer.setTimerType(2)
        err, schids = ts3lib.getServerConnectionHandlerList()
        for schid in schids:
            err, status = ts3lib.getConnectionStatus(schid)
            self.onConnectStatusChangeEvent(schid, status, err)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()

    def tick(self):
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.servers)
        if len(self.servers) < 1: self.timer.stop(); return
        for schid in self.servers:
            self.waitingForList.append(schid)
            ts3lib.requestComplainList(schid, 0, self.__class__.__name__)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            self.servers.pop(schid, None)
            if len(self.servers) < 1: self.timer.stop()
        elif newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.waitingForList.append(schid)
            ts3lib.requestComplainList(schid, 0, self.__class__.__name__)

    def onComplainListEvent(self, schid, targetClientDatabaseID, targetClientNickName, fromClientDatabaseID, fromClientNickName, complainReason, timestamp):
        if not schid in self.waitingForList and not schid in self.servers: return
        if not self.timer.isActive() and len(self.servers) == 1:
            self.timer.start(self.interval)
        if not schid in self.servers: self.servers[schid] = []
        complaint = (targetClientDatabaseID, fromClientDatabaseID)
        if not complaint in self.servers[schid]:
            self.servers[schid].append(complaint)
            (err, ownID) = ts3lib.getClientID(schid)
            ts3lib.requestClientPoke(schid, ownID, 'New complaint for "{}" by "{}"'.format(targetClientNickName, fromClientNickName))  # clientURL(schid, nickname=targetClientNickName), clientURL(schid, nickname=fromClientNickName)

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode != self.__class__.__name__: return False
        if error == ts3defines.ERROR_database_empty_result:
            if schid in self.servers:
                if len(self.servers[schid]) > 0: self.servers[schid].clear()
            else:
                self.servers[schid] = []
                if not self.timer.isActive() and len(self.servers) == 1:
                    self.timer.start(self.interval)
            return True
        elif error == ts3defines.ERROR_ok: return True
        return False

    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        if returnCode != self.__class__.__name__ or error != ts3defines.ERROR_permissions_client_insufficient or failedPermissionID != 207: return False
        if PluginHost.cfg.getboolean("general", "verbose"): print(self.name,">","not enough permissions on tab ", schid, "!")
        if schid in self.waitingForList: self.waitingForList.remove(schid)
        return True