from ts3plugin import ts3plugin
from datetime import datetime
from urllib.parse import quote as urlencode
import ts3defines, ts3lib, _ts3lib
from PythonQt.QtCore import QTimer
from bluscream import date, Time

def channelURL(schid=None, cid=0, name=None):
    if schid == None:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if name == None:
        try: (error, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
        except: name = cid
    return '[b][url=channelid://{0}]"{1}"[/url][/b]'.format(cid, name)
def clientURL(schid=None, clid=0, uid=None, nickname=None, encodednick=None):
    if schid == None:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if uid == None:
        try: (error, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        except: pass
    if nickname == None:
        try: (error, nickname) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        except: nickname = uid
    if encodednick == None:
        try: encodednick = urlencode(nickname)
        except: pass
    return '[url=client://{0}/{1}~{2}]{3}[/url]'.format(clid, uid, encodednick, nickname)


class showQueries(ts3plugin):
    name = "Query Viewer"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Shows you queries in channels.\n\nHomepage: https://github.com/Bluscream/Extended-Info-Plugin\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = "query"
    infoTitle = "[b]Queries:[/b]"
    menuItems = []
    hotkeys = []
    debug = False
    timer = QTimer()
    cleartimer = QTimer()
    schid = 0
    queries = []
    hqueries = []
    hqueries_cache = []
    query_uids = ["serveradmin", "ServerQuery"]
    waitingFor = ""
    retcode = ""

    def __init__(self):
        self.cleartimer.timeout.connect(self.clearQueries)
        self.cleartimer.start(1000*18000)
        if self.debug: ts3lib.printMessageToCurrentTab("[{0} {1}] [color=orange]{2}[/color] Plugin for pyTSon by [url=https://github.com/{3}]{4}[/url] loaded.".format(date(), Time(), self.name, self.author))

    def stop(self):
        self.timer.stop()
        self.timer = None
        del self.timer
        self.timer = QTimer()

    def onConnectStatusChangeEvent(self, schid, status, errorNumber):
        if status == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.schid = schid
            self.timer.timeout.connect(self.checkQueries)
            self.timer.start(1000)
            ts3lib.printMessageToCurrentTab('Timer started!')
        elif status == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if self.timer.isActive():
                self.timer.stop()
                self.schid = 0
                ts3lib.printMessageToCurrentTab('Timer stopped!')

    def checkQueries(self):
        (err, clist) = ts3lib.getClientList(self.schid)
        for c in clist:
            if c in self.queries:
                continue
            else:
                (err, ctype) = ts3lib.getClientVariable(self.schid, c, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
                if ctype != ts3defines.ClientType.ClientType_SERVERQUERY: continue
                self.queries.append(c)
                (err, cid) = ts3lib.getChannelOfClient(self.schid, c)
                # (err, channelname) = ts3lib.getChannelVariable(self.schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
                ts3lib.printMessage(self.schid, "<{0}> Found Query {1} in channel {2}".format(Time(), clientURL(self.schid, c), channelURL(self.schid, cid)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
        # self.waitingFor = self.query_uids[0]
        # self.retcode = ts3lib.createReturnCode()
        # ts3lib.requestClientIDs(self.schid, self.query_uids[0], self.retcode)

    def clearQueries(self):
        self.queries = []
        ts3lib.printMessage(self.schid, "<{0}> Cleared Query List".format(Time()), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)

    def infoData(self, schid, id, atype):
        try:
            if atype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
                (error, clist) = ts3lib.getChannelClientList(schid, id)
                i = []
                for c in clist:
                    (error, clienttype) = ts3lib.getClientVariable(schid, c, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
                    if clienttype == ts3defines.ClientType.ClientType_SERVERQUERY:
                        i.append(clientURL(schid, c))
                if len(i) < 1: return
                else: return i
        except: return

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        # if oldChannelID != 0: return
        (err, clienttype) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
        if clienttype != ts3defines.ClientType.ClientType_SERVERQUERY: return
        # (err, channelname) = ts3lib.getChannelVariable(schid, newChannelID, ts3defines.ChannelProperties.CHANNEL_NAME)
        if visibility == ts3defines.Visibility.ENTER_VISIBILITY:
            ts3lib.printMessage(schid, "<{0}> {1} enters view to channel {2}".format(Time(), clientURL(schid, clientID), channelURL(schid, newChannelID)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
        elif visibility == ts3defines.Visibility.LEAVE_VISIBILITY:
            ts3lib.printMessage(schid, "<{0}> {1} leaves from channel {2}{3}".format(Time(), clientURL(schid, clientID), channelURL(schid, oldChannelID), " ({})".format(moveMessage) if moveMessage else ""), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
        else: ts3lib.printMessage(schid, "<{0}> {1} switched from channel {2} to {3}".format(Time(), clientURL(schid, clientID), channelURL(schid, oldChannelID), channelURL(schid, newChannelID)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
        # <16:11:43> "charlie sheen" switched from channel "Intros Gratis <3" to "Serverteam-Gesucht Builder"

    def onClientIDsEvent(self, schid, uid, clid, nickname):
        # print('{0} == {1}: {2}'.format(uid, self.waitingFor, uid == self.waitingFor))
        if not uid == self.waitingFor: return
        (err, chan) = ts3lib.getChannelOfClient(schid, clid)
        if err != ts3defines.ERROR_ok: self.hqueries.append((clid, uid, nickname))

    def onClientIDsFinishedEvent(self, schid):
        if not self.waitingFor in self.query_uids: return
        if len(self.hqueries) > 0:
            # qstring = ", ".join("[url=client://{0}/{1}]{2}[/url]".format(tup) for tup in self.queries)
            qlist = ["[url=client://{}/{}]{}[/url]".format(*tup) for tup in self.hqueries]
            qstring = ", ".join(qlist)
            ts3lib.printMessage(schid, "<{0}> Found {1} hidden Queries with UID \"{2}\": {3}".format(Time(), len(self.hqueries), self.waitingFor, qstring), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
            self.hqueries = []
        if self.waitingFor == self.query_uids[0]:
            self.waitingFor = self.query_uids[-1]
            ts3lib.requestClientIDs(schid, self.query_uids[-1], self.retcode)
        if self.waitingFor == self.query_uids[-1]:
            self.waitingFor = False

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode == self.retcode: return True

    def printQueries(self):
        (err, schids) = ts3lib.getServerConnectionHandlerList()
        for schid in schids:
            (err, cids) = ts3lib.getChannelList(schid)
            for cid in cids:
                (err, clids) = ts3lib.getChannelClientList(schid, cid)
                msg = []
                for clid in clids:
                    (err, ctype) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
                    if ctype != ts3defines.ClientType.ClientType_SERVERQUERY: continue
                    msg.append(clientURL(schid, clid))
                if len(msg) < 1: continue
                ts3lib.printMessage(schid, "<{0}> {1} has [b]{2}[/b] Query Clients: {3}".format(Time(), channelURL(schid, cid), len(msg), ", ".join(msg)), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
            self.waitingFor = self.query_uids[0]
            self.retcode = ts3lib.createReturnCode()
            ts3lib.requestClientIDs(schid, self.query_uids[0], self.retcode)

    def processCommand(self, schid, cmd):
        cmd = cmd.split(' ', 1)
        command = cmd[0].lower()
        if command == "list":
            self.printQueries()
        return 1