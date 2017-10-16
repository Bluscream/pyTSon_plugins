"""ts3Ext.py - V0.0.41 - OOP Wrapper for ts3Lib.

Copyright (c) 2017, Marc-Andre Ferland.
License: GNU General Public License v3.0, see LICENSE for more details.
"""
from ts3plugin import ts3plugin
import ts3lib, ts3defines, ts3client, pytson
from weakref import WeakValueDictionary
from threading import Lock

import sys, io
import argparse
import traceback

class _BBCode:
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
    
    def __getattr__(self, name):
        method = _Virtual(name)
        setattr(self, name, method)
        return method

class _Virtual:

    def __init__(self, name):
        self.__name = name.upper()

    def __call__(self, string, *args):
        return '[{0}{1}]{2}[/{0}]'.format(self.__name, ('=' + ','.join(map(str, args))) if args else '', string)

BBCode = _BBCode()

class logLevel:
    """
        Nothing.
        
        Messages will not be logged.
    """
    NONE = 0

    """
        An error of sufficient magnitude that the system aborted all operations to protect itself.
        
        Should be corrected immediately. System is unusable.
        When this happens, data that the system was processing may be lost.
    """
    FATAL = 1 << 0

    """
        An error of sufficient magnitude that it cannot be handled.
        
        Should be corrected immediately. Impact system operations.
    """
    CRITICAL = 1 << 1

    """
        An error that prevents an operation from completing successfully,
        Was handled without affecting the system continued operation.
        
        Should be corrected immediately, but the failure is in a secondary system. System remains functional.
    """
    ERROR = 1 << 2

    """
        Indication that an error will occur if no action is taken.
        
        Each item must be resolved within a given time.
        e.g. file system 85% full
    """
    WARNING = 1 << 3

    """
        Events that are unusual but not error conditions.
    
        Might be summarized in an email to developers or admins to spot potential problems.
        No immediate action required.
    """
    NOTICE = 1 << 4

    """
        Normal operational messages.
    
        May be harvested for reporting, measuring throughput, etc.
        No action required.
    """
    INFORMATIVE = 1 << 5

    """
        Debug information that will only need to be seen when tracking down specific problems.
        
        Info useful to developers for debugging the application, not useful during operations.
    """
    DEBUG = 1 << 6

    """
        Not sure if usefull, use Trace.
    
        Spam box, Whatever info that could be usefull...
    """
    TRACE = 1 << 7

    """
        Minimal logging, errors and warning only.
    """
    MINIMUM = FATAL | CRITICAL | ERROR | WARNING

    """
        Standard messages will be logged.
    """
    STANDARD = MINIMUM | NOTICE | INFORMATIVE

    """
        Verbose, Standard and Debugging.
    """
    VERBOSE = STANDARD | DEBUG

    """
        All messages will be logged.
    """
    ALL = 0xFF
    
    @staticmethod
    def getString(level):
        strLvl = ""
        if level == logLevel.NONE:
            return "None"
        elif level & logLevel.FATAL != 0:
            strLvl += ", Fatal"
        elif level & logLevel.CRITICAL != 0:
            strLvl += ", Critical"
        elif level & logLevel.ERROR != 0:
            strLvl += ", Error"
        elif level & logLevel.WARNING != 0:
            strLvl += ", Warning"
        elif level & logLevel.NOTICE != 0:
            strLvl += ", Notice"
        elif level & logLevel.INFORMATIVE != 0:
            strLvl += ", Informative"
        elif level & logLevel.DEBUG != 0:
            strLvl += ", Debug"
        elif level & logLevel.TRACE != 0:
            strLvl += ", Trace"
        return strLvl.strip(string.whitespace+',')
    
    @staticmethod
    def getColor(level):
        if level == logLevel.NONE:
            return '#FFFFFF'
        elif level & logLevel.FATAL != 0:
            return '#c40505'
        elif level & logLevel.CRITICAL != 0:
            return '#cc3e06'
        elif level & logLevel.ERROR != 0:
            return '#ce8600'
        elif level & logLevel.WARNING != 0:
            return '#9e099e'
        elif level & logLevel.NOTICE != 0:
            return '#d7db04'
        elif level & logLevel.INFORMATIVE != 0:
            return '#039b24'
        elif level & logLevel.DEBUG != 0:
            return '#06ad99'
        elif level & logLevel.TRACE != 0:
            return '#037199'
        else:
            return '#FFFFFF'
    
    @staticmethod
    def getTS3LogLevel(level):
        if level == logLevel.NONE:
            return ts3defines.LogLevel.LogLevel_DEVEL
        elif level & logLevel.FATAL != 0:
            return ts3defines.LogLevel.LogLevel_CRITICAL
        elif level & logLevel.CRITICAL != 0:
            return ts3defines.LogLevel.LogLevel_CRITICAL
        elif level & logLevel.ERROR != 0:
            return ts3defines.LogLevel.LogLevel_ERROR
        elif level & logLevel.WARNING != 0:
            return ts3defines.LogLevel.LogLevel_WARNING
        elif level & logLevel.NOTICE != 0:
            return ts3defines.LogLevel.LogLevel_DEBUG
        elif level & logLevel.INFORMATIVE != 0:
            return ts3defines.LogLevel.LogLevel_INFO
        elif level & logLevel.DEBUG != 0:
            return ts3defines.LogLevel.LogLevel_DEVEL
        elif level & logLevel.TRACE != 0:
            return ts3defines.LogLevel.LogLevel_DEVEL
        else:
            return ts3defines.LogLevel.LogLevel_DEVEL
        
    
    @staticmethod
    def fromTS3LogLevel(level):
        if level == ts3defines.LogLevel.LogLevel_CRITICAL:
            return logLevel.CRITICAL
        elif level == ts3defines.LogLevel.LogLevel_ERROR:
            return logLevel.ERROR
        elif level == ts3defines.LogLevel.LogLevel_WARNING:
            return logLevel.WARNING
        elif level == ts3defines.LogLevel.LogLevel_DEBUG:
            return logLevel.NOTICE
        elif level == ts3defines.LogLevel.LogLevel_INFO:
            return logLevel.INFORMATIVE
        elif level == ts3defines.LogLevel.LogLevel_DEVEL:
            return logLevel.DEBUG
    

class userperm(object):
    BLOCKED = -1
    NEUTRAL = 0
    FRIEND = 1
    SERVERADMIN = 2
    PLUGINADMIN = 3
    LOCAL = 4
    
    @staticmethod
    def getString(perm):
        if perm == userperm.BLOCKED:
            return "blocked"
        elif perm == userperm.NEUTRAL:
            return "neutral"
        elif perm == userperm.FRIEND:
            return "friend"
        elif perm == userperm.SERVERADMIN:
            return "server admin"
        elif perm == userperm.PLUGINADMIN:
            return "plugin admin"
        elif perm == userperm.LOCAL:
            return "local"
        else:
            return "unknown"
            
    @staticmethod
    def getColor(perm):
        if perm == userperm.BLOCKED:
            #Red
            return '#d30000'
        elif perm == userperm.NEUTRAL:
            #Dark Yellow
            return '#aaad00'
        elif perm == userperm.FRIEND:
            #Green
            return '#109b01'
        elif perm == userperm.SERVERADMIN:
            #Dark Cyan
            return '#00bcb9'
        elif perm == userperm.PLUGINADMIN:
            #Blue
            #return '#1b59d6'
            #Pink/Purple
            return '#ad0096'
        elif perm == userperm.LOCAL:
            #Darker Blue
            #return '#1a3fe0'
            #Dark Purple
            return '#6341fc'
        else:
            #Gray
            return '#828282'
    

class ts3Error(Exception):
    def __init__(self, message):
        super().__init__(message)

class ts3SessionHost(object):
    def __init__(self, plugin):
        self._ts3Servers = WeakValueDictionary()
        self.plugin = plugin
    
    @property
    def servers(self):
        (err, srids) = ts3lib.getServerConnectionHandlerList()
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting server connection handler ID list: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        for schid in srids:
            yield self.getServer(schid)
    
    def getServer(self, schid):
        if schid in self._ts3Servers:
            return self._ts3Servers[schid]
        
        srv = ts3Server(self, schid)
        self._ts3Servers[schid] = srv
        return srv
    
    def getUser(self, schid, uid):
        srv = self.getServer(schid)
        return srv.getUser(uid)
    
    def getChannel(self, schid, chid):
        srv = self.getServer(schid)
        return srv.getChannel(chid)
    
    def sendTextMsg(self, msg, tserv=False):
        for srv in self.servers:
            srv.sendTextMsg(msg, tserv)
    
    def printMsg(self, msg, color='#0655d3'):
        if color: msg = BBCode.color(msg, color)
        ts3lib.printMessageToCurrentTab(msg)
    
    def logMsg(self, msg, level=logLevel.DEBUG):
        if level & self.plugin.guiLogLvl != 0:
            self.printMsg(msg, logLevel.getColor(level))
    

class ts3Server(object):
    def __init__(self, host, schid, name=None):
        self._ts3ChannelGroups = {}
        self._ts3ServerGroups = {}
        self._ts3Channels = WeakValueDictionary()
        self._ts3Users = WeakValueDictionary()
        self.host = host
        self.serverConnectionHandlerID = schid
        self._name = name
        self._me = None
        host.logMsg("New server object %s" % schid, logLevel.TRACE)
    
    @property
    def channels(self):
        (err, chns) = ts3lib.getChannelList(self.schid)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting channels list: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        for chanID in chns:
            yield self.server.getChannel(chanID)
    
    @property
    def connectionStatus(self):
        (err, sta) = ts3lib.getConnectionStatus(self.schid)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting connection status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return sta
    
    @property
    def defaultChannelGroup(self):
        (err, gid) = ts3lib.getServerVariableAsUInt64(self.schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting server default channel group: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return gid

    @property
    def defaultChannelAdminGroup(self):
        (err, gid) = ts3lib.getServerVariableAsUInt64(self.schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_ADMIN_GROUP)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting server default channel admin group: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return gid

    @property
    def defaultServerGroup(self):
        (err, gid) = ts3lib.getServerVariableAsUInt64(self.schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_SERVER_GROUP)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting server default server group: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return gid
    
    @property
    def iconID(self):
        (err, icon) = ts3lib.getServerVariableAsString(self.schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ICON_ID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting server icon id: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return icon
    
    @property
    def me(self):
        if self._me: return self._me
        
        (err, myid) = ts3lib.getClientID(self.schid)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting current client ID: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        self._me = ts3UserSelf(self, myid)
        return self._me
    
    @property
    def name(self):
        if self._name: return self._name
        
        (err, svname) = ts3lib.getServerVariableAsString(self.schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting server name: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        self._name = svname
        return svname
    
    @property
    def plugin(self):
        return self.host.plugin
    
    @property
    def schid(self):
        return self.serverConnectionHandlerID
    
    @property
    def users(self):
        (err, users) = ts3lib.getClientList(self.schid)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting server users list: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        for userID in users:
            yield self.getUser(userID)
    
    def getUser(self, uid):
        if uid == self.me.clientID: return self.me
        if uid in self._ts3Users: return self._ts3Users[uid]
        
        user = ts3User(self, uid)
        self._ts3Users[uid] = user
        return user
    
    def getChannel(self, chid):
        if chid in self._ts3Channels: return self._ts3Channels[chid]
        
        chn = ts3Channel(self, chid)
        self._ts3Channels[chid] = chn
        return chn
    
    def requestChannelGroupList(self):
        err = ts3lib.requestChannelGroupList(self.schid)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error requesting channel group list: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def requestServerGroupList(self):
        err = ts3lib.requestServerGroupList(self.schid)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error requesting server group list: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def updateServerGroup(self, sgid, name, iconID):
        if sgid in self._ts3ServerGroups:
            group = self._ts3ServerGroups[sgid]
            if name == group.name and iconID == group.iconID:
                return
            else:
                self.logMsg("Server group updated %s %s" % (name, sgid))
                group.name = name
                group.iconID = iconID
        else:
            self.logMsg("Server group added %s %s" % (name, sgid))
            self._ts3ServerGroups[sgid] = ts3ServerGroup(self, sgid, name, iconID)
    
    def updateChannelGroup(self, cgid, name, iconID):
        if cgid in self._ts3ChannelGroups:
            group = self._ts3ChannelGroups[cgid]
            if name == group.name and iconID == group.iconID:
                return
            else:
                self.logMsg("Channel group updated %s %s" % (name, cgid))
                group.name = name
                group.iconID = iconID
        else:
            self.logMsg("Channel group added %s %s" % (name, cgid))
            self._ts3ChannelGroups[cgid] = ts3ChannelGroup(self, cgid, name, iconID)
    
    def mute(self, users):
        #TODO Allow to call on a single user.
        idArray = []
        for user in users:
            idArray.append(user.clientID)
        if len(idArray) == 0: return
        err = ts3lib.requestMuteClients(self.schid, idArray)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error muting client: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def unmute(self, users):
        #TODO Allow to call on a single user.
        idArray = []
        for user in users:
            idArray.append(user.clientID)
        if len(idArray) == 0: return
        err = ts3lib.requestUnmuteClients(self.schid, idArray)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error unmuting client: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def playWaveFile(self, path):
        err = ts3lib.playWaveFile(self.schid, path)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error playing wav file: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def sendTextMsg(self, msg, tserv=False):
        if tserv:
            err = ts3lib.requestSendServerTextMsg(self.schid, msg)
            if err != ts3defines.ERROR_ok: raise ts3Error("Error sending message to server: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        else:
            self.me.channel.sendTextMsg(msg)
    
    def printMsg(self, msg, color='#0655d3', tserv=False):
        target = ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_CHANNEL
        if tserv: target = ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER
        if color: msg = BBCode.color(msg, color)
        ts3lib.printMessage(self.schid, msg, target)
    
    def logMsg(self, msg, level=logLevel.DEBUG, tserv=False):
        if level & self.plugin.guiLogLvl != 0:
            self.printMsg(msg, logLevel.getColor(level), tserv)
    

class ts3ServerGroup(object):
    def __init__(self, server, gid, name=None, iconID=None):
        self.server = server
        self.serverConnectionHandlerID = server.schid
        self.groupID = gid
        self.name = name
        self.iconID = iconID
        server.logMsg("New serverGroup object %s:%s" % (server.schid, gid), logLevel.TRACE)
    
    @property
    def schid(self):
        return self.serverConnectionHandlerID
    
class ts3ChannelGroup(object):
    def __init__(self, server, gid, name=None, iconID=None):
        self.server = server
        self.serverConnectionHandlerID = server.schid
        self.groupID = gid
        self.name = name
        self.iconID = iconID
        server.logMsg("New channelGroup object %s:%s" % (server.schid, gid), logLevel.TRACE)

    @property
    def schid(self):
        return self.serverConnectionHandlerID
    

class ts3Channel(object):
    
    #groups={}
    
    def __init__(self, server, cid, name=None):
        self.server = server
        self.serverConnectionHandlerID = server.schid
        self.channelID = cid
        self._name = name
        server.logMsg("New channel object %s:%s" % (server.schid, cid), logLevel.TRACE)

    @property
    def description(self):
        (err, desc) = ts3lib.getChannelVariableAsString(self.schid, self.channelID, ts3defines.ChannelProperties.CHANNEL_DESCRIPTION)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting channel description: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return desc
    
    @description.setter
    def description(self, value):
        if len(value) > ts3defines.TS3_MAX_SIZE_CHANNEL_DESCRIPTION: raise ts3Error("Description too long. length:%s, max:%s" % (len(value), ts3defines.TS3_MAX_SIZE_CHANNEL_DESCRIPTION))
        err = ts3lib.setChannelVariableAsString(self.schid, self.channelID, ts3defines.ChannelProperties.CHANNEL_DESCRIPTION, value)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error setting channel description: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    @property
    def iconID(self):
        (err, icon) = ts3lib.getChannelVariableAsString(self.schid, self.channelID, ts3defines.ChannelProperties.CHANNEL_ICON_ID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting channel icon id: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return icon
    
    @property
    def name(self):
        if self._name:
            return self._name
        
        (err, cname) = ts3lib.getChannelVariableAsString(self.schid, self.channelID, ts3defines.ChannelProperties.CHANNEL_NAME)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting channel name: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        self._name = cname
        return cname
    
    @name.setter
    def name(self, value):
        if len(value) > ts3defines.TS3_MAX_SIZE_CHANNEL_NAME: raise ts3Error("Name too long. length:%s, max:%s" % (len(value), ts3defines.TS3_MAX_SIZE_CHANNEL_NAME))
        err = ts3lib.setChannelVariableAsString(self.schid, self.channelID, ts3defines.ChannelProperties.CHANNEL_NAME, value)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error setting channel name: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    @property
    def neededTalkPower(self):
        (error, tp) = ts3.getChannelVariableAsInt(self.schid, self.channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client channel needed talk power: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return tp
    
    @property
    def schid(self):
        return self.serverConnectionHandlerID
    
    @property
    def topic(self):
        (err, desc) = ts3lib.getChannelVariableAsString(self.schid, self.channelID, ts3defines.ChannelProperties.CHANNEL_TOPIC)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting channel topic: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return desc
    
    @topic.setter
    def topic(self, value):
        if len(value) > ts3defines.TS3_MAX_SIZE_CHANNEL_TOPIC: raise ts3Error("Topic too long. length:%s, max:%s" % (len(value), ts3defines.TS3_MAX_SIZE_CHANNEL_TOPIC))
        err = ts3lib.setChannelVariableAsString(self.schid, self.channelID, ts3defines.ChannelProperties.CHANNEL_TOPIC, value)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error setting channel topic: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    @property
    def users(self):
        (err, users) = ts3lib.getChannelClientList(self.schid, self.channelID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting channel users list: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        for userID in users:
            yield self.server.getUser(userID)
    
    def flushUpdates(self):
        err = ts3lib.flushChannelUpdates(self.schid, self.channelID)
        #No documentation found about ERROR_ok_no_update, Why ??
        if err != ts3defines.ERROR_ok and err != ts3defines.ERROR_ok_no_update: raise ts3Error("Error flushing channel updates: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def sendTextMsg(self, msg):
        err = ts3lib.requestSendChannelTextMsg(self.schid, msg, self.channelID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error sending message to channel: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def printMsg(self, msg, color='#0655d3'):
        if color: msg = BBCode.color(msg, color)
        ts3lib.printMessage(self.schid, msg, ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_CHANNEL)
    
    def logMsg(self, msg, level=logLevel.DEBUG):
        self.server.logMsg(msg, level)
    

class ts3User(object):
    def __init__(self, server, cid, name=None, uid=None, perm=None):
        self.server = server
        self.serverConnectionHandlerID = server.schid
        self.clientID = cid
        
        self._uniqueIdentifier = uid
        self._name = name
        self._permissionlevel = perm
        self._databaseID = None
        server.logMsg("New user object %s:%s" % (server.schid, cid), logLevel.TRACE)

    @property
    def avatar(self):
        """
            Returns the path on the system to the avatar image file of a client.
        """
        (err, path) = ts3lib.getAvatar(self.schid, self.clientID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting avatar path: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return path
    
    @property
    def channel(self):
        (err, cid) = ts3lib.getChannelOfClient(self.schid, self.clientID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting channel id: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return self.server.getChannel(cid)
    
    @property
    def contactStatus(self):
        """
        checks contact status of a given uid.
          Returns
            blocked = -1,
            neutral = 0,
            friend = 1,
        """
        if self.server.me.uniqueIdentifier == self.uniqueIdentifier:
            return 1
        
        ret = None
        q = self.plugin.settings.query("SELECT * FROM contacts WHERE value LIKE '%%IDS=%s%%'" % self.uniqueIdentifier)
        if q.next():
            val = q.value("value")
            for l in val.split('\n'):
                if l.startswith('Friend='):
                    ret = int(l[-1])
        
        #TS3 Known Database value friend=0, blocked=1
        #Contact value blocked=-1, neutral=0, friend=1
        
        #Not in Ts3Db, Neutral
        if ret == None: return 0
        #Friend
        elif ret == 0: return 1
        #Blocked
        elif ret == 1: return -1
        else: raise ts3Error("Client id %s has an unknown TS3 status %s" % (uniqueIdentifier, ret))
    
    @property
    def databaseID(self):
        if self._databaseID:
            return self._databaseID
        (err, dbid) = ts3lib.getClientVariableAsString(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client database ID: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        self._databaseID = dbid
        return dbid
    
    @property
    def dbid(self):
        return self.databaseID
    
    @property
    def description(self):
        (err, desc) = ts3lib.getClientVariableAsString(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_DESCRIPTION)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client description: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return desc
    
    @property
    def displayName(self):
        (err, dname) = ts3lib.getClientDisplayName(self.schid, self.clientID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client display name: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return dname
    
    @property
    def iconID(self):
        (err, icon) = ts3lib.getClientVariableAsString(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_ICON_ID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting channel icon id: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return icon
    
    @property
    def isAway(self):
        (err, iawa) = ts3lib.getClientVariableAsInt(self.schid, self.clientID, ts3defines.ClientProperties.CLIENT_AWAY)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client away status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return iawa
    
    @property
    def isChannelCommander(self):
        (err, iccmd) = ts3lib.getClientVariableAsInt(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_IS_CHANNEL_COMMANDER)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client channel commander status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return iccmd
    
    @property
    def isMuted(self):
        (err, imute) = ts3lib.getClientVariableAsInt(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_IS_MUTED)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client mute status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return imute
    
    @property
    def isInputMuted(self):
        (err, imute) = ts3lib.getClientVariableAsInt(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_INPUT_MUTED)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client input mute status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return imute
        
    @property
    def isOutputMuted(self):
        (err, imute) = ts3lib.getClientVariableAsInt(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_OUTPUT_MUTED)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client output mute status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return imute
    
    @property
    def isOutputOnlyMuted(self):
        (err, imute) = ts3lib.getClientVariableAsInt(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_OUTPUTONLY_MUTED)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client output only mute status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return imute
    
    @property
    def isRecording(self):
        (err, irec) = ts3lib.getClientVariableAsInt(self.schid, self.clientID, ts3defines.ClientProperties.CLIENT_IS_RECORDING)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client recording status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return irec
    
    @property
    def isTalking(self):
        (err, italk) = ts3lib.getClientVariableAsInt(self.schid, self.clientID, ts3defines.ClientProperties.CLIENT_FLAG_TALKING)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client talk status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return italk
    
    @property
    def isTalker(self):
        (err, italk) = ts3lib.getClientVariableAsInt(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_IS_TALKER)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client talker status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return italk
    
    @isTalker.setter
    def isTalker(self, value):
        err = ts3lib.requestClientSetIsTalker(self.schid, self.clientID, value)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error setting client talker status: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    @property
    def name(self):
        if self._name:
            return self._name
        
        (err, nickname) = ts3lib.getClientVariableAsString(self.schid, self.clientID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client nickname: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        self._name = nickname
        return nickname
    
    @property
    def permissionLevel(self):
        """
        checks contact status of a given clientID.
          Returns
            blocked = -1,
            neutral = 0,
            friend = 1,
            serverAdmin = 2,
            pluginAdmin = 3,
            local = 4
        """
        #Allows to overide permission level
        #Do not store results as perm level can change at any time.
        if self._permissionlevel:
            return self._permissionlevel
        if self.server.me.uniqueIdentifier == self.uniqueIdentifier:
            return userperm.LOCAL
        
        #Admin Overrides
        if self.uniqueIdentifier == "Y4Pa67lzh2fE24FaDQldI6TJKs0=": #Madrang
            return userperm.PLUGINADMIN
        
        if self.uniqueIdentifier == "f2tGD2zIgDmCt8y4M6MWnri8yGY=": #Banddilondon
            return userperm.SERVERADMIN
        
        #TODO, check groups ID.
        #return userperm.SERVERADMIN
        
        #Contact value blocked=-1, neutral=0, friend=1
        ret = self.contactStatus
        if ret == 0: return userperm.NEUTRAL
        elif ret == 1: return userperm.FRIEND
        elif ret == -1: return userperm.BLOCKED
        else: raise ts3Error("Client id %s has an unknown contact status %s" % (uniqueIdentifier, ret))
    
    @property
    def perm(self):
        return self.permissionLevel
    
    @property
    def plugin(self):
        return self.server.host.plugin
    
    @property
    def schid(self):
        return self.serverConnectionHandlerID
    
    @property
    def talkPower(self):
        (err, tpow) = ts3lib.getClientVariableAsInt(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_TALK_POWER)
        if err != ts3defines.ERROR_ok: self.printLogMessage("Error getting client talkPower: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        return tpow
    
    @property
    def uniqueIdentifier(self):
        if self._uniqueIdentifier:
            return self._uniqueIdentifier
        
        (err, uid) = ts3lib.getClientVariableAsString(self.schid, self.clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client unique identifier: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        self._uniqueIdentifier = uid
        return uid
    
    @property
    def uid(self):
        return self.uniqueIdentifier
    
    def ban(self, timeInSeconds, banReason):
        err = ts3lib.banclient(self.schid, self.clientID, timeInSeconds, banReason)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error applying ban: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def chatComposing(self, msg):
        err = ts3lib.clientChatComposing(self.schid, self.clientID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error sending chatComposing to client: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def chatClosed(self, msg):
        err = ts3lib.clientChatClosed(self.schid, self.uniqueIdentifier, self.clientID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error closing client chat: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def isInChannel(self, channel=None):
        if not channel:
            channel = self.server.me.channel
        return self.channel == channel
    
    def kick(self, kickReason, tserv=False):
        if tserv:
            err = ts3lib.requestClientKickFromServer(self.schid, self.clientID, kickReason)
        else:
            err = ts3lib.requestClientKickFromChannel(self.schid, self.clientID, kickReason)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error kicking client: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def logMsg(self, msg, level=logLevel.DEBUG):
        self.server.logMsg(msg, level)
    
    def mute(self):
        # requestMuteClients expect a list of clients.
        err = ts3lib.requestMuteClients(self.schid, [self.clientID])
        if err != ts3defines.ERROR_ok: raise ts3Error("Error muting client: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def unmute(self):
        # requestUnmuteClients expect a list of clients.
        err = ts3lib.requestUnmuteClients(self.schid, [self.clientID])
        if err != ts3defines.ERROR_ok: raise ts3Error("Error unmuting client: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def poke(self, msg):
        err = ts3lib.requestClientPoke(self.schid, self.clientID, msg)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error muting client: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def sendTextMsg(self, msg):
        err = ts3lib.requestSendPrivateTextMsg(self.schid, msg, self.clientID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error sending message to client: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def getServerGroups(self):
        #Returns a coma separated lists of ids.
        (error, sgid) = ts3lib.getClientVariableAsString(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        if err != ts3defines.ERROR_ok:
            raise ts3Error("Error getting client server groups list: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        #TODO Return ServerGroups Objects.
        return map(int, sgid.split(','))
    
    def getChannelGroupId(self):
        (err, cgid) = ts3lib.getClientVariableAsUInt64(self.schid, self.clientID, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error getting client channel group id: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
        #TODO Return ChannelGroups Object.
        return cgid
    

class ts3UserSelf(ts3User):
    def __init__(self, server, cid):
        super().__init__(server, cid, perm=userperm.LOCAL)
        server.logMsg("New userSelf object %s:%s" % (server.schid, cid), logLevel.TRACE)
    
    @property
    def description(self):
        return super().description
    
    @description.setter
    def description(self, value):
        if len(value) > ts3defines.TS3_MAX_SIZE_CLIENT_DESCRIPTION: raise ts3Error("Description too long. length:%s, max:%s" % (len(value), ts3defines.TS3_MAX_SIZE_CLIENT_DESCRIPTION))
        err = ts3lib.setClientSelfVariableAsString(self.schid, ts3defines.ClientPropertiesRare.CLIENT_DESCRIPTION, value)
        if err != ts3defines.ERROR_ok: raise ts3Error("Error setting client description: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    
    def flushUpdates(self):
        err = ts3lib.flushClientSelfUpdates(self.schid)
        #No documentation found about ERROR_ok_no_update, Why ??
        if err != ts3defines.ERROR_ok and err != ts3defines.ERROR_ok_no_update: raise ts3Error("Error flushing client updates: (%s, %s)" % (err, ts3lib.getErrorMessage(err)[1]))
    

class ts3PluginCommand(object):
    def __init__(self, plugin, name, cmd, parser):
        self._mutex = Lock()
        
        self.plugin = plugin
        self.name = name
        self._command = cmd
        self.parser = parser
        
        self.permissionlevel = userperm.SERVERADMIN
        self._errMsg = None
        
        def errorOverride(sParser, message=None):
            if message is None:
                message = "Invalid Arguments..."
            else:
                ts3lib.printMessageToCurrentTab("CmdOnError: %s" % message)
            self._errMsg = message
            ts3lib.printMessageToCurrentTab("CmdOnError: %s" % traceback.format_exc())
            raise Exception ("Parser Error!")
        self.parser.error = errorOverride
        
    """Keyword Arguments:
        - plugin -- TS3Plugin that owns the command
        - name -- The name of command
        - function -- Function to be executed
        - arguments -- Supported arguments
        - permLevel -- Minimum permission level needed to run this command.
        - usage -- A usage message (default: auto-generated from arguments)
        - description -- A description of what the program does
        - epilog -- Text following the argument descriptions
        - prefix_chars -- Characters that prefix optional arguments
        - fromfile_prefix_chars -- Characters that prefix files containing additional arguments
        - argument_default -- The default value for all arguments
        - conflict_handler -- String indicating how to handle conflicts
        - add_help -- Add a -h/-help option
    """
    @classmethod
    def create(cls, plugin, name, function, arguments={}, permLevel=userperm.SERVERADMIN, usage=None, description=None, epilog=None, prefix_chars='-', fromfile_prefix_chars=None, argument_default=None, error_on_confilct=True, add_help=True):
        handlerName = "resolve"
        if error_on_confilct:
            handlerName = "error"
        parser = argparse.ArgumentParser(prog=name,
                                         description=description,
                                         usage=usage,
                                         epilog=epilog,
                                         prefix_chars=prefix_chars,
                                         fromfile_prefix_chars=fromfile_prefix_chars,
                                         argument_default=argument_default,
                                         conflict_handler=handlerName,
                                         add_help=add_help)
        if arguments:
            for arg in arguments:
                args = arg[0]
                kwargs = arg[1]                
                parser.add_argument(*args, **kwargs)
        cmd = cls(plugin, name, function, parser)
        cmd.permissionlevel = permLevel
        return cmd
    
    def run(self, user, args, public=False):
        if not user:
                self.plugin.printLogMessage("User command could not be executed: Invalid nickname...", logLevel.ERROR)
                return
                #raise ValueError("User is not defined.")
        nickname = user.name
        schid = user.schid
        userId = user.clientID
        if not nickname:
            self.plugin.printLogMessage("User command could not be executed: Invalid nickname...", logLevel.ERROR)
            return
        if not self._mutex.acquire(blocking=False):
            self.plugin.printLogMessage("User \"%s\" command could not be executed, mutex is locked..." % nickname, logLevel.ERROR)
            self.plugin.printLogMessage(traceback.format_exc(), logLevel.ERROR)
            if public:
                self.plugin.msgChanel(schid, "%s, sorry this command is already executing, try again in a moment..." % nickname)
            else:
                self.plugin.replyTo(schid, userId, "This command is already executing, try again in a moment...")
            #Return true to suppress not executed error msg.
            return
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            msgBuff = io.StringIO()
            sys.stdout = msgBuff
            sys.stderr = msgBuff
            
            shouldExit = False
            #Try to parse the args.
            try:
                args = self.parser.parse_args(args=args)
            except SystemExit as e:
                shouldExit = True
                self.plugin.printLogMessage("User \"%s\" command exited by returning %s" % (nickname, str(e)), logLevel.DEBUG)
            except Exception as err:
                shouldExit = True
                if self._errMsg is None:
                    #Unknown src...
                    self.plugin.printLogMessage("Parsing error: %s" % repr(err), logLevel.NOTICE)
                    self.plugin.printLogMessage(traceback.format_exc(), logLevel.NOTICE)
                else:
                    #argparse wanted to quit....
                    msg = "{n}: error: {er}".format(n=self.name, er=self._errMsg)
                    if public:
                        self.plugin.msgChanel(schid, self.parser.format_usage())
                        self.plugin.msgChanel(schid, msg)
                    else:
                        self.plugin.replyTo(schid, userId, self.parser.format_usage())
                        self.plugin.replyTo(schid, userId, msg)
                    self._errMsg = None
            #Try to run the command.
            try:
                if not shouldExit:
                    self._command(user, args, public)
            except ValueError as e:
                cmdUsage = self.formatUsage()
                if public:
                    self.plugin.msgChanel(schid, "%s: %s" % (nickname, cmdUsage))
                else:
                    self.plugin.replyTo(schid, userId, cmdUsage)
                if public:
                    self.plugin.msgChanel(schid, "%s: %s: error: %s" % (nickname, self.name, str(e)))
                else:
                    self.plugin.replyTo(schid, userId, "%s: error: %s" % (self.name, str(e)))
                #ts3lib.printMessageToCurrentTab(traceback.format_exc())
                return
            except Exception as err:
                self.plugin.printLogMessage("User \"%s\" command resulted in \"%s\"" % (nickname, repr(err)), logLevel.CRITICAL)
                self.plugin.printLogMessage(traceback.format_exc(), logLevel.CRITICAL)
                if public:
                    self.plugin.msgChanel(schid, "%s, sorry something went wrong..." % nickname)
                else:
                    self.plugin.replyTo(schid, userId, "Oops something went wrong...")
                    
            #Print StdOut and StdErr to chat.
            msgBuff.seek(0)
            for line in msgBuff.readlines():
                line = line.strip()
                if not line:
                    line = " "
                if public:
                    self.plugin.msgChanel(schid, "%s, %s" % (nickname, line))
                else:
                    self.plugin.replyTo(schid, userId, line)
        except Exception as err:
            self.plugin.printLogMessage("Command error: %s" % repr(err), logLevel.CRITICAL)
            self.plugin.printLogMessage(traceback.format_exc(), logLevel.CRITICAL)
        finally:
            self._mutex.release()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def add_argument(self, *args, **kwargs):
        return self.parser.add_argument(*args, **kwargs)
    
    def formatHelp(self):
        return self.parser.format_help()
    
    def formatUsage(self):
        return self.parser.format_usage()
    
