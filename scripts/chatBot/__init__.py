from configparser import ConfigParser
from os import path
from urllib.parse import quote as urlencode
from PythonQt.QtCore import *
from PythonQt.QtGui import *
from ts3plugin import ts3plugin
import datetime, ts3defines, ts3lib, sys, os, pytson, pytsonui
import time as timestamp
from base64 import b64encode, b64decode
from pytsonui import setupUi
from pytson import *

class color(object):
    DEFAULT = "[color=white]"
    DEBUG = "[color=grey]"
    INFO = "[color=lightblue]"
    SUCCESS = "[color=green]"
    WARNING = "[color=orange]"
    ERROR = "[color=red]"
    FATAL = "[color=darkred]"
    ENDMARKER = "[/color]"

class chatBot(ts3plugin):
    name = "Chat Bot"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "A simple chatbot for Teamspeak 3 Clients"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    ini = path.join(pytson.getPluginPath(), "scripts", "chatBot", "settings.ini")
    cfg = ConfigParser()
    cmdini = path.join(pytson.getPluginPath(), "scripts", "chatBot", "commands.ini")
    cmd = ConfigParser()
    # cmdpy = path.join(pytson.getPluginPath(), "scripts", "chatBot")
    dlg = None
    color = []
    cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}
    lastcmd = {"cmd": "", "params": "", "time": 0, "user": 0}
    returnCode = ""
    noperms = []
    tmpsgroups = []
    tmpcgroups = []

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = {"cfgversion": "1", "debug": "False", "enabled": "True", "customprefix": "True", "prefix": "!", "unknowncmd": "True"}
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        if path.isfile(self.cmdini):
            self.cmd.read(self.cmdini)
        else:
            self.cmd['about'] = {"enabled": "True", "function": "commandAbout"}
            self.cmd['help'] = {"enabled": "False", "function": "commandHelp"}
            with open(self.cmdini, 'w') as configfile:
                self.cmd.write(configfile)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def configure(self, qParentWidget):
        try:
            if not self.dlg: self.dlg = SettingsDialog(self.ini, self.cfg, self.cmdini, self.cmd)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
            if path.isfile(self.ini):
                self.cfg.read(self.ini)
        except:
            from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon")

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentiﬁer, message, ﬀIgnored):
        try:
            if ffIgnored: return False
            (error, ownID) = ts3lib.getClientID(schid)
            lasttime = int(self.lastcmd["time"])
            time = int(timestamp.time())
            (error, _clid) = ts3lib.getClientID(schid)
            if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT and toID != _clid: return
            # if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL and toID != _cid: return False
            # ts3lib.printMessageToCurrentTab(self.clientURL(schid, _clid))
            # ts3lib.printMessageToCurrentTab(message)
            # ts3lib.printMessageToCurrentTab("%s"%message.startswith(self.clientURL(schid, _clid)))
            # ts3lib.printMessageToCurrentTab("%s"%str(self.clientURL(schid, _clid) in message.strip()))
            if message.startswith(self.cfg.get('general', 'prefix')) and self.cfg.getboolean('general', 'customprefix'):
                command = message.split(self.cfg.get('general', 'prefix'), 1)[1]
            elif message.startswith(self.clientURL(schid, _clid)) and not self.cfg.getboolean('general', 'customprefix'):
                command = message.split(self.clientURL(schid, _clid), 1)[1]
            else: return False
            if PluginHost.cfg.getboolean("general", "verbose"):
                ts3lib.printMessageToCurrentTab("{0}".format(self.lastcmd))
                ts3lib.printMessageToCurrentTab("time: {0}".format(time))
                ts3lib.printMessageToCurrentTab("time -5: {0}".format(time - 5))
                ts3lib.printMessageToCurrentTab("lasttime: {0}".format(lasttime))
            if lasttime > time - 5: ts3lib.printMessageToCurrentTab("is time -5: True")
            cmd = command.split(' ', 1)[0].lower()
            if not cmd in self.cmd.sections():
                if self.cfg.getboolean("general", "unknowncmd"): self.answerMessage(schid, targetMode, toID, fromID, "Command %s does not exist." % cmd)
                return False
            if not self.cmd.getboolean(cmd, "enabled"):
                if self.cfg.getboolean("general", "disabledcmd"): self.answerMessage(schid, targetMode, toID, fromID, "Command %s is disabled." % cmd)
                return False
            params = ""
            _params = ""
            try: _params = command.split(' ', 1)[1].strip()
            except: pass
            if _params != "": params = _params  # ;params = bytes(_params, "utf-8").decode("unicode_escape")
            self.lastcmd = {"cmd": cmd, "params": params, "time": int(timestamp.time()), "user": fromID}
            ts3lib.printMessageToCurrentTab("{0}".format(self.lastcmd))
            if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL: (
            error, toID) = ts3lib.getChannelOfClient(schid, _clid)
            evalstring = "self.%s(%s,%s,%s,%s,'%s')" % (
            self.cmd.get(cmd, "function"), schid, targetMode, toID, fromID, params)
            eval(evalstring)
        except:
            from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
            if schid in self.noperms: self.noperms.remove(schid)

    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        if self.returnCode == returnCode and error == 2568 and failedPermissionID == 217: self.noperms.extend([schid])

    def answerMessage(self, schid, targetMode, toID, fromID, message, hideprefix=False):
        if schid in self.noperms: ts3lib.printMessageToCurrentTab("Insufficient permissions to answer message from {0}".format(fromID)); return
        message = [message[i:i + 1024] for i in range(0, len(message), 1024)]
        if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT:
            for msg in message: self.returnCode = ts3lib.createReturnCode(); ts3lib.requestSendPrivateTextMsg(schid, msg, fromID, self.returnCode)
        elif targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL:
            if hideprefix:
                for msg in message: self.returnCode = ts3lib.createReturnCode(); ts3lib.requestSendChannelTextMsg(schid, "{0}".format(msg), toID, self.returnCode)
            else:
                for msg in message: self.returnCode = ts3lib.createReturnCode(); ts3lib.requestSendChannelTextMsg(schid, "[url=client://]@[/url]%s: %s" % ( self.clientURL(schid, fromID), msg), toID, self.returnCode)

    def clientURL(self, schid=None, clid=0, uid=None, nickname=None, encodednick=None):
        if schid == None:
            try: schid = ts3lib.getCurrentServerConnectionHandlerID()
            except: pass
        if uid == None:
            try: (error, uid) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            except: pass
        if nickname == None:
            try: (error, nickname) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
            except: nickname = uid
        if encodednick == None:
            try: encodednick = urlencode(nickname)
            except: pass
        return "[url=client://%s/%s~%s]%s[/url]" % (clid, uid, encodednick, nickname)

    # YOUR COMMANDS HERE:

    def commandAbout(self, schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, "%s v%s by %s" % (self.name, self.version, self.author))

    def commandHelp(self, schid, targetMode, toID, fromID, params=""):
        _cmds = "\n"
        if self.cfg.getboolean('general', 'customprefix'):
            prefix = self.cfg.get('general', 'prefix')
        else:
            (error, id) = ts3lib.getClientID(schid);prefix = self.clientURL(schid, id)
        for command in self.cmd.sections():
            if self.cmd.getboolean(command, "enabled"):
                _cmds += prefix + str(command) + "\n"
            else:
                _cmds += prefix + str(command) + " (Disabled)\n"
        self.answerMessage(schid, targetMode, toID, fromID, "Available commands for %s v%s:%s" % (self.name, self.version, _cmds), True)

    def commandToggle(self, schid, targetMode, toID, fromID, params=""):
        (error, ownID) = ts3lib.getClientID(schid)
        if not fromID == ownID: return
        self.cmd.set(params, "enabled", str(not self.cmd.getboolean(params, "enabled")))
        self.answerMessage(schid, targetMode, toID, fromID, "Set command {0} to {1}".format(params, self.cmd.getboolean(params, "enabled")))

    def commandEval(self, schid, targetMode, toID, fromID, params=""):
        (error, ownID) = ts3lib.getClientID(schid)
        if not fromID == ownID: return
        try:
            ev = eval(params)
            self.answerMessage(schid, targetMode, toID, fromID, "Evalualated {0}successfully{1}:\n{2}".format(color.SUCCESS, color.ENDMARKER, ev))
        except TypeError as e:
            if e.strerror == "eval() arg 1 must be a string, bytes or code object":
                self.answerMessage(schid, targetMode, toID, fromID,
                                   "%s%s evalualated successfully: %s" % (color.SUCCESS, params, ev))
            else:
                from traceback import format_exc;
                self.answerMessage(schid, targetMode, toID, fromID, format_exc())
        except SyntaxError as e:
            if e.strerror == "unexpected EOF while parsing":
                self.answerMessage(schid, targetMode, toID, fromID,
                                   "%s%s evalualated successfully: %s" % (color.SUCCESS, params, ev))
            else:
                from traceback import format_exc;
                self.answerMessage(schid, targetMode, toID, fromID, format_exc())
        except: from traceback import format_exc; self.answerMessage(schid, targetMode, toID, fromID, format_exc())

    def commandTime(self, schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, 'My current time is: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))

    def commandUnix(self, schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, datetime.datetime.utcfromtimestamp(int(params)).strftime('%Y-%m-%d %H:%M:%S'))

    def commandTaskList(self, schid, targetMode, toID, fromID, params=""):
        import psutil
        msg = []
        for p in psutil.process_iter():
            try:
                _p = str(p.as_dict(attrs=['name'])['name'])
                if ".exe" in _p.lower(): msg.extend([_p])
            except psutil.Error: pass
        msg = '\n'.join(sorted(msg))
        self.answerMessage(schid, targetMode, toID, fromID, msg)

    def idByName(self,ids,name):
        for i in ids:
            if name.lower() in i["name"].lower(): return i["id"]
        return False

    def commandToggleServerGroup(self, schid, targetMode, toID, fromID, params=""):
        self.cmdevent = {"event": "onServerGroupListEvent", "returnCode": "", "schid": schid, "targetMode": targetMode, "toID": toID, "fromID": fromID, "params": params}
        ts3lib.requestServerGroupList(schid)

    def onServerGroupListEvent(self, schid, serverGroupID, name, atype, iconID, saveDB):
        try:
            if not self.cmdevent["event"] == "onServerGroupListEvent": return
            self.tmpsgroups.append({"id": serverGroupID, "name": name})
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onServerGroupListFinishedEvent(self, schid):
        try:
            sgid = self.idByName(self.tmpsgroups,self.cmdevent["params"])
            if not sgid: self.answerMessage(schid, self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], "Failed to find a servergroup like \"%s\""%self.cmdevent["params"]);return
            (error, dbid) = ts3lib.getClientVariableAsInt(schid, self.cmdevent["fromID"], ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
            (error, sgroups) = ts3lib.getClientVariableAsString(schid, self.cmdevent["fromID"], ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
            sgroups = [int(n) for n in sgroups.split(",")]
            if sgid in sgroups: _p = "added";p = "Adding"; error = ts3lib.requestServerGroupDelClient(schid, sgid, dbid)
            else: _p = "removed";p = "Removing"; error = ts3lib.requestServerGroupAddClient(schid, sgid, dbid)
            if error == ts3defines.ERROR_ok: _t = "Successfully {0} servergroup #{1}".format(_p, sgid)
            else: _t = "{0} Servergroup #{1} failed!".format(p, sgid)
            self.answerMessage(schid, self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], _t)
            self.tmpsgroups = []
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
        self.cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}

    def commandOP(self, schid, targetMode, toID, fromID, params=""):
        target = int(params)
        (error, dbid) = ts3lib.getClientVariableAsInt(schid, target, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        (error, chan) = ts3lib.getChannelOfClient(schid, target)
        (error, name) = ts3lib.getChannelVariableAsString(schid, chan, ts3defines.ChannelProperties.CHANNEL_NAME)
        error = ts3lib.requestSetClientChannelGroup(schid, [11], [chan], [dbid])
        if error == ts3defines.ERROR_ok:
            _t = "You have been made operator of the channel [url=channelid://{0}]{1}[/url].".format(chan,name)
            self.answerMessage(schid, ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT, toID, target, _t)

    def commandSetChannelGroup(self, schid, targetMode, toID, fromID, params=""):
        self.cmdevent = {"event": "onChannelGroupListEvent", "returnCode": "", "schid": schid, "targetMode": targetMode, "toID": toID, "fromID": fromID, "params": params}
        self.tmpcgroups = []
        ts3lib.requestChannelGroupList(schid)

    def onChannelGroupListEvent(self, schid, channelGroupID, name, atype, iconID, saveDB):
        try:
            if not self.cmdevent["event"] == "onChannelGroupListEvent" or not atype == 1: return
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("atype: {0}".format(atype))
            self.tmpcgroups.append({"id": channelGroupID, "name": name})
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onChannelGroupListFinishedEvent(self, schid):
        try:
            id = self.idByName(self.tmpcgroups,self.cmdevent["params"])
            if not id: self.answerMessage(schid, self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], "Failed to find a channelgroup like \"%s\""%self.cmdevent["params"]);return
            (error, dbid) = ts3lib.getClientVariableAsInt(schid, self.cmdevent["fromID"], ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
            (error, own) = ts3lib.getClientID(schid)
            (error, chan) = ts3lib.getChannelOfClient(schid, own)
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("dbid: {0} | own: {1} | chan: {2} | id: {3}".format(dbid,own,chan,id))
            error = ts3lib.requestSetClientChannelGroup(schid, [id], [chan], [dbid])
            if error == ts3defines.ERROR_ok: _t = "Successfully set your channelgroup to #{0}".format(id)
            else: _t = "Setting your channelgroup #{0} failed!".format(id)
            self.answerMessage(schid, self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], _t)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
        self.cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}

    def commandSay(self, schid, targetMode, toID, fromID, params=""):
        if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT:
            ts3lib.requestSendPrivateTextMsg(schid, params, fromID)
        elif targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL:
            ts3lib.requestSendChannelTextMsg(schid, "{0}: {1}".format(self.clientURL(schid, fromID), params), toID)

    def commandMessage(self, schid, targetMode, toID, fromID, params=""):
        params = params.split(" ",1);target = int(params[0]);message = params[1]
        ts3lib.requestSendPrivateTextMsg(schid, "Message from {0}: {1}".format(self.clientURL(schid, fromID), message), target)

    def commandChannelMessage(self, schid, targetMode, toID, fromID, params=""):
        try:
            _p = params.split(" ",1);target = int(_p[0]);message = _p[1]
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Found Channel ID: {0}".format(target))
        except:
            (error, target) = ts3lib.getChannelOfClient(schid, fromID);message = params
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Found No Channel ID.")
        (error, ownID) = ts3lib.getClientID(schid)
        (error, ownChan) = ts3lib.getChannelOfClient(schid, ownID)
        if not ownChan == target: ts3lib.requestClientMove(schid, ownID, target, "123")
        ts3lib.requestSendChannelTextMsg(schid, "Message from {0}: {1}".format(self.clientURL(schid, fromID), message), target)
        if not ownChan == target: ts3lib.requestClientMove(schid, ownID, ownChan, "123")

    def commandPing(self, schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, "Pong!")

    def commandWhoAmI(self, schid, targetMode, toID, fromID, params=""):
        (error, displayName) = ts3lib.getClientDisplayName(schid, fromID)
        self.answerMessage(schid, targetMode, toID, fromID, "I changed your nickname to: %s%s" % (color.ERROR, displayName))

    def commandChannelKickMe(self, schid, targetMode, toID, fromID, params=""):
        if self.cfg.getboolean('general', 'customprefix'):
            prefix = self.cfg.get('general', 'prefix')
        else:
            (error, id) = ts3lib.getClientID(schid);prefix = self.clientURL(schid, id)
        (error, nickname) = ts3lib.getClientVariableAsString(schid, fromID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if params != "": ts3lib.requestClientKickFromChannel(schid, fromID, params)
        else: ts3lib.requestClientKickFromChannel(schid, fromID, "Command %sckickme used by %s" % (prefix, nickname))

    def commandChannelBanMe(self, schid, targetMode, toID, fromID, params=""):
        (error, ownID) = ts3lib.getClientID(schid)
        if self.cfg.getboolean('general', 'customprefix'): prefix = self.cfg.get('general', 'prefix')
        else: prefix = self.clientURL(schid, ownID)
        (error, nickname) = ts3lib.getClientVariableAsString(schid, fromID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        (error, dbid) = ts3lib.getClientVariableAsInt(schid, fromID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        (error, chan) = ts3lib.getChannelOfClient(schid, ownID)
        if params == "": params = "Command %scbanme used by %s" % (prefix, nickname)
        ts3lib.requestSetClientChannelGroup(schid, [12], [chan], [dbid])
        ts3lib.requestClientKickFromChannel(schid, fromID, params)

    def commandKickMe(self, schid, targetMode, toID, fromID, params=""):
        if self.cfg.getboolean('general', 'customprefix'):
            prefix = self.cfg.get('general', 'prefix')
        else:
            (error, id) = ts3lib.getClientID(schid);prefix = self.clientURL(schid, id)
        (error, nickname) = ts3lib.getClientVariableAsString(schid, fromID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if params != "": ts3lib.requestClientKickFromServer(schid, fromID, params)
        else: ts3lib.requestClientKickFromServer(schid, fromID, "Command %skickme used by %s" % (prefix, nickname))

    def commandBanMe(self, schid, targetMode, toID, fromID, params=""):
        if self.cfg.getboolean('general', 'customprefix'):
            prefix = self.cfg.get('general', 'prefix')
        else:
            (error, id) = ts3lib.getClientID(schid);prefix = self.clientURL(schid, id)
        (error, nickname) = ts3lib.getClientVariableAsString(schid, fromID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if params != "": _params = params.split(' ', 1)
        delay = 1;
        delay = _params[0]
        if len(_params) > 1: ts3lib.banclient(schid, fromID, int(delay), _params[1])
        else: ts3lib.banclient(schid, fromID, int(delay), "Command %sbanme used by %s" % (prefix, nickname))

    def commandQuit(self, schid, targetMode, toID, fromID, params=""):
        try: import sys;sys.exit()
        except: pass
        try: QApplication.quit()
        except: pass
        try: QCoreApplication.instance().quit()
        except: pass

    def commandDisconnect(self, schid, targetMode, toID, fromID, params=""):
        if self.cfg.getboolean('general', 'customprefix'):
            prefix = self.cfg.get('general', 'prefix')
        else:
            (error, id) = ts3lib.getClientID(schid);prefix = self.clientURL(schid, id)
        (error, nickname) = ts3lib.getClientVariableAsString(schid, fromID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if params != "":
            ts3lib.stopConnection(schid, params)
        else:
            ts3lib.stopConnection(schid, "Command %sdisconnect used by %s" % (prefix, nickname))

    def commandConnect(self, schid, targetMode, toID, fromID, params=""):
        params = params.split(' ', 1)
        ip = params[0].split(':')
        nickname = ""
        if params[1]: nickname = params[1]
        ts3lib.stopConnection(schid, "Connecting to %s" % ip)
        ts3lib.startConnection(schid, "", ip[0], int(ip[1]), nickname, [], "", "")

    def commandVersion(self, schid, targetMode, toID, fromID, params=""): pass

    def commandToggleRecord(self, schid, targetMode, toID, fromID, params=""):
        (error, clid) = ts3lib.getClientID(schid)
        (error, recording) = ts3lib.getClientVariableAsInt(schid, clid, ts3defines.ClientProperties.CLIENT_IS_RECORDING)
        if not recording:
            ts3lib.startVoiceRecording(schid)
        elif recording:
            ts3lib.stopVoiceRecording(schid)

    def commandNick(self, schid, targetMode, toID, fromID, params=""):
        ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, params)
        ts3lib.ﬂushClientSelfUpdates(schid)

    def commandBanList(self, schid, targetMode, toID, fromID, params=""):
        # try:
        returnCode = ts3lib.createReturnCode()
        self.cmdevent = {"event": "onBanListEvent", "returnCode": returnCode, "schid": schid, "targetMode": targetMode, "toID": toID, "fromID": fromID, "params": params}
        self.banlist = ""
        QTimer.singleShot(2500, self.sendBanList)
        ts3lib.requestBanList(schid)

    # except:

    def onBanListEvent(self, schid, banid, ip, name, uid, creationTime, durationTime, invokerName, invokercldbid, invokeruid, reason, numberOfEnforcements, lastNickName):
        item = ""
        item += "#%s" % banid
        if name: item += " | Name: %s" % name
        if ip: item += " | IP: %s" % ip
        if uid: item += " | UID: %s" % uid
        if reason: item += " | Reason: %s" % reason
        self.banlist += "\n%s" % item


    def sendBanList(self):
        ts3lib.requestSendPrivateTextMsg(self.cmdevent.schid, "%s" % self.banlist, self.cmdevent.fromID)
        self.answerMessage(self.cmdevent.schid, self.cmdevent.targetMode, self.cmdevent.toID, self.cmdevent.fromID, "%s" % self.banlist)
        self.cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}

    def commandMessageBox(self, schid, targetMode, toID, fromID, params=""):
        msgBox = QMessageBox()
        # if params.lower().startswith("[url]"):
        # params = params.split("[URL]")[1]
        # params = params.split("[/URL]")[0]
        # msgBox.setIconPixmap(QPixMap(params));
        # else:
        msgBox.setText(params)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.exec()

    def commandGoogle(self, schid, targetMode, toID, fromID, params=""):
        try:
            from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
            from urllib.parse import quote_plus
            googleAPI = "https://www.googleapis.com/customsearch/v1"
            googleAPIKey = "AIzaSyDj5tgIBtdiL8pdVV_tqm7aw45jjdFP1hw"
            googleSearchID = "008729515406769090877:33fok_ycoaa"
            params = quote_plus(params)
            url = "{0}?key={1}&cx={2}&q={3}".format(googleAPI, googleAPIKey, googleSearchID, params)
            self.nwmc = QNetworkAccessManager()
            self.nwmc.connect("finished(QNetworkReply*)", self.googleReply)
            self.cmdevent = {"event": "", "returnCode": "", "schid": schid, "targetMode": targetMode, "toID": toID, "fromID": fromID, "params": params}
            self.nwmc.get(QNetworkRequest(QUrl(url)))
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)


    def googleReply(self, reply):
        try:
            import json;from PythonQt.QtNetwork import QNetworkRequest, QNetworkReply
            results = json.loads(reply.readAll().data().decode('utf-8'))["items"]
            for result in results:
                self.answerMessage(self.cmdevent["schid"], self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], "[url={0}]{1}[/url]".format(result["link"],result["title"]), True)
            self.cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def commandFlood(self, schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, "Flooding {0} started...".format(params))

    def commandFindMe(self, schid, targetMode, toID, fromID, params=""):
        (error, ownID) = ts3lib.getClientID(schid)
        if not fromID == ownID: self.answerMessage(schid, targetMode, toID, fromID, "Insufficient permissions to run this command");return

    def commandLookup(self, schid, targetMode, toID, fromID, params=""):
        try:
            from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
            from urllib.parse import quote_plus
            lookupAPI = "https://api.opencnam.com/v3/phone/"
            lookupSID = "ACda22b69608b743328772059d32b63f26"
            lookupAuthToken = "AUc9d9217f20194053bf2989c7cb75a368"
            if params.startswith("00"): params = params.replace("00", "+", 1)
            params = quote_plus(params)
            url = "{0}{1}?format=json&casing=title&service_level=plus&geo=rate&account_sid={2}&auth_token={3}".format(lookupAPI, params, lookupSID, lookupAuthToken)
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Requesting: {0}".format(url))
            self.nwmc = QNetworkAccessManager()
            self.nwmc.connect("finished(QNetworkReply*)", self.lookupReply)
            self.cmdevent = {"event": "", "returnCode": "", "schid": schid, "targetMode": targetMode, "toID": toID, "fromID": fromID, "params": params}
            self.nwmc.get(QNetworkRequest(QUrl(url)))
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def lookupReply(self, reply):
        try:
            import json;from PythonQt.QtNetwork import QNetworkRequest, QNetworkReply
            result = json.loads(reply.readAll().data().decode('utf-8'))
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Result: {0}".format(result))
            try: self.answerMessage(self.cmdevent["schid"], self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], "{0}: {1} ({2}$/min)".format(result["number"],result["name"],result["price"]), True)
            except: self.answerMessage(self.cmdevent["schid"], self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], "{0}{1}{2} ({3})".format(color.ERROR, result["err"], color.ENDMARKER,self.cmdevent["params"]))
            self.cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def commandRegister(self, schid, targetMode, toID, fromID, params=""):
        (error, uid) = ts3lib.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
        if uid == "QTRtPmYiSKpMS8Oyd4hyztcvLqU=": # GommeHD
            (error, uid) = ts3lib.getClientVariableAsString(schid, int(params), ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            self.answerMessage(schid, targetMode, toID, int(params), ""+
            "Um dich auf diesem Teamspeak Server zu registrieren musst du folgendes tun:\n\n"+
            "1. Auf den Minecraft Server [color=green]gommehd.net[/color] joinen.\n"+
            "2. In den Minecraft chat [color=red]/ts set {0}[/color] eingeben.\n".format(uid)+
            "3. Im Teamspeak Chat dem User [URL=client://0/serveradmin~Gomme-Bot]Gomme-Bot[/URL] deinen Minecraft Namen schreiben (Groß/Kleinschreibung beachten)\n"+
            "4. Wenn die Registrierung erfolgreich warst erhälst du die Server Gruppe \"Registriert\". Es kann eine Zeit lang dauern bis dein Minecraft Kopf hinter deinem Namen erscheint.")
        elif uid == "U3UjHePU9eZ9bvnzIyLff4lvXBM=": pass
        else: self.answerMessage(schid, targetMode, toID, fromID, "Server not recognized or does not have a registration feature.")

    def commandDoxx(self, schid, targetMode, toID, fromID, params=""):
        try:
            from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
            url = "https://randomuser.me/api/?gender={0}&nat=de&noinfo".format(params.split(" ")[1])
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Requesting: {0}".format(url))
            self.nwmc = QNetworkAccessManager()
            self.nwmc.connect("finished(QNetworkReply*)", self.doxxReply)
            self.cmdevent = {"event": "", "returnCode": "", "schid": schid, "targetMode": targetMode, "toID": toID, "fromID": fromID, "params": params}
            self.nwmc.get(QNetworkRequest(QUrl(url)))
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def doxxReply(self, reply):
        try:
            import json;from PythonQt.QtNetwork import QNetworkRequest, QNetworkReply;from random import randint
            result = json.loads(reply.readAll().data().decode('utf-8'))["results"][0]
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Result: {0}".format(result))
            params = self.cmdevent["params"].split(" ")
            (error, name) = ts3lib.getClientVariableAsString(int(self.cmdevent["schid"]), int(params[0]), ts3defines.ClientProperties.CLIENT_NICKNAME)
            (error, uid) = ts3lib.getClientVariableAsString(int(self.cmdevent["schid"]), int(params[0]), ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            #try:
            self.answerMessage(self.cmdevent["schid"], self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"],
                "\nTS Name: [url=http://ts3index.com/?page=searchclient&nickname={0}]{0}[/url] | UID: [url=http://ts3index.com/?page=searchclient&uid={1}]{1}[/url]\n".format(name, uid)+
                "{0} {1}\n".format(result["name"]["first"], result["name"]["last"]).title()+
                "{0} {1}\n".format(result["location"]["street"][5:],randint(0,50)).title()+
                "{0} {1}\n".format(result["location"]["postcode"],result["location"]["city"]).title()+
                "☎ {0} ({1})\n".format(result["phone"],result["cell"])+
                "[url=https://adguardteam.github.io/AnonymousRedirect/redirect.html?url={0}]Bild 1[/url]\n".format(result["picture"]["large"]), True)
            #except: self.answerMessage(self.cmdevent["schid"], self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], "Unable to doxx {0}".format(name))
            self.cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    perms = {}
    def commandPerms(self, schid, targetMode, toID, fromID, params=""):
        self.cmdevent = {"event": "onPermissionListEvent", "returnCode": "", "schid": schid, "targetMode": targetMode, "toID": toID, "fromID": fromID, "params": params}
        ts3lib.requestPermissionList(schid)

    def onPermissionListEvent(self, schid, permissionID, permissionName, permissionDescription):
        #ts3lib.printMessageToCurrentTab("self.name: {0}".format(self.__name__))
        if self.cmdevent["event"] == "onPermissionListEvent" and self.cmdevent["schid"] == schid:
            ts3lib.printMessageToCurrentTab("#{0} | {1} | {2}".format(permissionID, permissionName, permissionDescription))
            #self.perms

    def onPermissionListFinishedEvent(self, serverConnectionHandlerID):
        ts3lib.printMessageToCurrentTab("{0}".format(self.perms))
        self.cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}

    def commandWhois(self, schid, targetMode, toID, fromID, params=""):
        try:
            from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
            from urllib.parse import quote_plus
            params = quote_plus(params)
            url = "https://jsonwhois.com/api/v1/whois?domain={0}".format(params)
            token = "fe1abe2646bdc7fac3d36a688d1685fc"
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Requesting: {0}".format(url))
            request = QNetworkRequest()
            request.setHeader( QNetworkRequest.ContentTypeHeader, "application/json" );
            request.setRawHeader("Authorization", "Token token={0}".format(token));
            request.setUrl(QUrl(url))
            self.nwmc = QNetworkAccessManager()
            self.nwmc.connect("finished(QNetworkReply*)", self.whoisReply)
            self.cmdevent = {"event": "", "returnCode": "", "schid": schid, "targetMode": targetMode, "toID": toID, "fromID": fromID, "params": params}
            self.nwmc.get(request)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def whoisReply(self, reply):
        try:
            import json;from PythonQt.QtNetwork import QNetworkRequest, QNetworkReply
            result = json.loads(reply.readAll().data().decode('utf-8'))
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Result: {0}".format(result))
            try: self.answerMessage(self.cmdevent["schid"], self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], "Registrant: {0} | Admin: {1} | Tech: {2}".format(result["registrant_contacts"][0]["name"],result["admin_contacts"][0]["name"],result["technical_contacts"][0]["name"]), True)
            except: self.answerMessage(self.cmdevent["schid"], self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], "{0}{1}{2}".format(color.ERROR, result["status"], color.ENDMARKER))
            self.cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    oldChannelID = 0
    def commandJoin(self, schid, targetMode, toID, fromID, params=""):
        (error, target) = ts3lib.getChannelOfClient(schid, fromID)
        (error, ownID) = ts3lib.getClientID(schid)
        (error, ownChan) = ts3lib.getChannelOfClient(schid, ownID)
        if not ownChan == target: ts3lib.requestClientMove(schid, ownID, target, "123")

    def commandBack(self, schid, targetMode, toID, fromID, params=""):
        (error, ownID) = ts3lib.getClientID(schid)
        ts3lib.requestClientMove(schid, ownID, self.oldChannelID, "123")
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("self.oldChannelID: {0}".format(self.oldChannelID))

    def commandB64Encode(self, schid, targetMode, toID, fromID, params=""):
        try: msg = b64encode(params.encode('utf-8')).decode('utf-8')
        except Exception as ex: msg = "Error while encoding: {}".format(ex.__class__.__name__)
        self.answerMessage(schid, targetMode, toID, fromID, msg)

    def commandB64Decode(self, schid, targetMode, toID, fromID, params=""):
        try: msg = b64decode(params.encode('utf-8')).decode('utf-8')
        except Exception as ex: msg = "Error while decoding: {}".format(ex.__class__.__name__)
        self.answerMessage(schid, targetMode, toID, fromID, msg)

    def commandShutdown(self, schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, "Executing \"shutdown -s -f -t 60\"")
        os.system('shutdown -s -f -t 60')

    def commandAbortShutdown(self, schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, "Executing \"shutdown -a\"")
        os.system('shutdown -a')

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        (error, _clid) = ts3lib.getClientID(schid)
        if clientID == _clid and not oldChannelID == 0: self.oldChannelID = oldChannelID

    # COMMANDS END

class SettingsDialog(QDialog):
        def __init__(self, ini, cfg, cmdini, cmd, parent=None):
            try:
                self.ini = ini
                self.cfg = cfg
                self.cmdini = cmdini
                self.cmd = cmd
                super(QDialog, self).__init__(parent)
                self.setAttribute(Qt.WA_DeleteOnClose)
                setupUi(self, path.join(getPluginPath(), "scripts", "chatBot", "settings.ui"))
                self.setWindowTitle("Chat Bot Settings")
                # header = self.tbl_commands.horizontalHeader()
                # header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
                # header.setResizeMode(1, QtGui.QHeaderView.Stretch)
                # header.setResizeMode(2, QtGui.QHeaderView.Stretch)
                # self.tbl_commands.setColumnWidth(0, 25)
                self.chk_enabled.setChecked(cfg.getboolean("general", "enabled"))
                self.chk_debug.setChecked(cfg.getboolean("general", "debug"))
                self.chk_unknowncmd.setChecked(cfg.getboolean("general", "unknowncmd"))
                self.chk_disabledcmd.setChecked(cfg.getboolean("general", "disabledcmd"))
                self.grp_prefix.setChecked(cfg.getboolean("general", "customprefix"))
                self.txt_prefix.setText(cfg.get("general", "prefix"))
                self.loadCommands()
            except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

        def loadCommands(self):
            self.tbl_commands.clear()
            self.tbl_commands.setRowCount(len(self.cmd.sections()))
            row = 0
            for i in self.cmd.sections():
                item = QTableWidgetItem(i)
                kitem = QTableWidgetItem(self.cmd[i]["function"])
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                item.setCheckState(Qt.Checked if self.cmd.getboolean(i, "enabled") else Qt.Unchecked)
                self.tbl_commands.setItem(row, 1, kitem)
                self.tbl_commands.setItem(row, 0, item)
                row += 1
            self.tbl_commands.setRowCount(row)
            self.tbl_commands.sortItems(0)

        def on_btn_add_clicked(self):
            self.tbl_commands.insertRow(self.tbl_commands.rowCount() + 1)

        # ok = BoolResult(); newurl = QInputDialog.getText(self, "Change url of repository %s" % name, "Url:", QLineEdit.Normal, rep["url"], ok)
        # if ok: rep["url"] = newurl
        def on_btn_remove_clicked(self):
            self.tbl_commands.removeRow(self.tbl_commands.selectedRows()[0])

        def on_btn_apply_clicked(self):
            try:
                self.cfg.set('general', 'enabled', str(self.chk_enabled.isChecked()))
                self.cfg.set('general', 'debug', str(self.chk_debug.isChecked()))
                self.cfg.set('general', 'unknowncmd', str(self.chk_unknowncmd.isChecked()))
                self.cfg.set('general', 'disabledcmd', str(self.chk_disabledcmd.isChecked()))
                self.cfg.set('general', 'customprefix', str(self.grp_prefix.isChecked()))
                self.cfg.set('general', 'prefix', self.txt_prefix.text)
                with open(self.ini, 'w') as configfile:
                    self.cfg.write(configfile)
                i = 0
                while i < self.tbl_commands.rowCount:
                    try:
                        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}".format(self.tbl_commands.item(i, 0)))
                        if not self.tbl_commands.item(i, 0).text() in self.cmd.sections(): self.cmd.add_section(i)
                        self.cmd.set(self.tbl_commands.item(i, 0).text(), "function", self.tbl_commands.item(i, 1).text())
                        self.cmd.set(self.tbl_commands.item(i, 0).text(), "enabled", str(self.tbl_commands.item(i, 0).checkState() == Qt.Checked))
                    except:
                        from traceback import format_exc;ts3lib.logMessage("Could not add row {0} to commands.ini\n{1}".format(i, format_exc()), ts3defines.LogLevel.LogLevel_INFO, "pyTSon Chat Bot", 0)
                    i += 1
                with open(self.cmdini, 'w') as configfile:
                    self.cmd.write(configfile)
                self.loadCommands();
            except:
                from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

        def on_btn_close_clicked(self):
            self.close()

class chatCommand(object):
    """
    name = "__ts3plugin__"
    version = "1.0"
    author = "Thomas \"PLuS\" Pathmann"
    description = "This is the baseclass for all ts3 python plugins"
    """

    def __init__(self):
        pass

    def stop(self):
        pass
