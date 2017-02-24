from configparser import ConfigParser
from os import path
from urllib.parse import quote as urlencode
from PythonQt.QtCore import *
from PythonQt.QtGui import *
from pytsonui import setupUi
from ts3plugin import ts3plugin
import datetime, ts3defines, ts3lib, sys, os


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
    apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "A simply chatbot for Teamspeak 3 Clients"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = False
    ini = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "chatBot", "settings.ini")
    cfg = ConfigParser()
    cmdini = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "chatBot", "commands.ini")
    cmd = ConfigParser()
    # cmdpy = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "chatBot")
    dlg = None
    color = []
    cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = {"cfgversion": "1", "debug": "False", "enabled": "True", "customprefix": "True",
                                   "prefix": "!"}
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        if path.isfile(self.cmdini):
            self.cmd.read(self.cmdini)
        else:
            self.cmd['about'] = {"enabled": "True", "function": "commandAbout"}
            self.cmd['help'] = {"enabled": "True", "function": "commandHelp"}
            self.cmd['eval'] = {"enabled": "True", "function": "commandEval"}
            self.cmd['time'] = {"enabled": "True", "function": "commandTime"}
            with open(self.cmdini, 'w') as configfile:
                self.cmd.write(configfile)
        ts3lib.logMessage(self.name + " script for pyTSon by " + self.author + " loaded from \"" + __file__ + "\".",
                          ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(
            datetime.datetime.now()) + " [color=orange]" + self.name + "[/color] Plugin for pyTSon by [url=https://github.com/" + self.author + "]" + self.author + "[/url] loaded.")

    def configure(self, qParentWidget):
        try:
            if not self.dlg: self.dlg = SettingsDialog(self.ini, self.cfg, self.cmdini, self.cmd)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
        except:
            from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR,
                                                               "PyTSon", 0)

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentiﬁer, message, ﬀIgnored):
        try:
            if ffIgnored: return False
            (error, _clid) = ts3lib.getClientID(schid)
            if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT and toID != _clid: return False
            # if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL and toID != _cid: return False
            # ts3lib.printMessageToCurrentTab(self.clientURL(schid, _clid))
            # ts3lib.printMessageToCurrentTab(message)
            # ts3lib.printMessageToCurrentTab("%s"%message.startswith(self.clientURL(schid, _clid)))
            # ts3lib.printMessageToCurrentTab("%s"%str(self.clientURL(schid, _clid) in message.strip()))
            if message.startswith(self.cfg.get('general', 'prefix')) and self.cfg.getboolean('general', 'customprefix'):
                command = message.split(self.cfg.get('general', 'prefix'), 1)[1]
            elif message.startswith(self.clientURL(schid, _clid)) and not self.cfg.getboolean('general',
                                                                                              'customprefix'):
                command = message.split(self.clientURL(schid, _clid), 1)[1]
            else:
                return False
            cmd = command.split(' ', 1)[0].lower()
            if not cmd in self.cmd.sections(): self.answerMessage(schid, targetMode, toID, fromID,
                                                                  "Command %s does not exist." % cmd);return False
            params = ""
            _params = ""
            try:
                _params = command.split(' ', 1)[1]
            except:
                pass
            if _params != "": params = _params  # ;params = bytes(_params, "utf-8").decode("unicode_escape")
            if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL: (
            error, toID) = ts3lib.getChannelOfClient(schid, _clid)
            evalstring = "self.%s(%s,%s,%s,%s,'%s')" % (
            self.cmd.get(cmd, "function"), schid, targetMode, toID, fromID, params)
            # ts3lib.printMessageToCurrentTab(evalstring)
            eval(evalstring)
        except:
            from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR,
                                                               "PyTSon", 0)

    def answerMessage(self, schid, targetMode, toID, fromID, message):
        message = [message[i:i + 1024] for i in range(0, len(message), 1024)]
        if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT:
            for msg in message: ts3lib.requestSendPrivateTextMsg(schid, msg, fromID)
        elif targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL:
            for msg in message: ts3lib.requestSendChannelTextMsg(schid, "[url=client://]@[/url]%s: %s" % (self.clientURL(schid, fromID), msg), toID)

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
        for command in self.cmd.sections(): _cmds += prefix + str(command) + "\n"
        self.answerMessage(schid, targetMode, toID, fromID,
                           "Available commands for %s v%s:%s" % (self.name, self.version, _cmds))

    def commandEval(self, schid, targetMode, toID, fromID, params=""):
        try:
            ev = eval(params)
            self.answerMessage(schid, targetMode, toID, fromID,
                               "%s%s evalualated successfully: %s" % (color.SUCCESS, params, ev))
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
        except:
            from traceback import format_exc;
            self.answerMessage(schid, targetMode, toID, fromID, format_exc())

    def commandTime(self, schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, 'My current time is: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))

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

    def commandTogglesServerGroup(self, schid, targetMode, toID, fromID, params=""):
        returnCode = ts3lib.createReturnCode()
        self.cmdevent = {"event": "onServerGroupListEvent", "returnCode": returnCode, "schid": schid, "targetMode": targetMode, "toID": toID, "fromID": fromID, "params": params}
        self.tmpsgroups = []
        (error, sgroups) = ts3lib.requestServerGroupList(schid, returnCode)

    def commandSay(self, schid, targetMode, toID, fromID, params=""):
        if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT:
            ts3lib.requestSendPrivateTextMsg(schid, params, fromID)
        elif targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL:
            ts3lib.requestSendChannelTextMsg(schid, "%s: %s" % (self.clientURL(schid, fromID), params), toID)

    def commandPing(self, schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, "Pong!")

    def commandWhoAmI(self, schid, targetMode, toID, fromID, params=""):
        (error, displayName) = ts3lib.getClientDisplayName(schid, fromID)
        self.answerMessage(schid, targetMode, toID, fromID, "I changed your nickname to: %s%s" % (color.ERROR, displayName))

    def commandKickMe(self, schid, targetMode, toID, fromID, params=""):
        if self.cfg.getboolean('general', 'customprefix'):
            prefix = self.cfg.get('general', 'prefix')
        else:
            (error, id) = ts3lib.getClientID(schid);prefix = self.clientURL(schid, id)
        (error, nickname) = ts3lib.getClientVariableAsString(schid, fromID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if params != "":
            ts3lib.requestClientKickFromServer(schid, fromID, params)
        else:
            ts3lib.requestClientKickFromServer(schid, fromID, "Command %skickme used by %s" % (prefix, nickname))

    def commandBanMe(self, schid, targetMode, toID, fromID, params=""):
        if self.cfg.getboolean('general', 'customprefix'):
            prefix = self.cfg.get('general', 'prefix')
        else:
            (error, id) = ts3lib.getClientID(schid);prefix = self.clientURL(schid, id)
        (error, nickname) = ts3lib.getClientVariableAsString(schid, fromID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if params != "": _params = params.split(' ', 1)
        delay = 1;
        delay = _params[0]
        if len(_params) > 1:
            ts3lib.banclient(schid, fromID, int(delay), _params[1])
        else:
            ts3lib.banclient(schid, fromID, int(delay), "Command %sbanme used by %s" % (prefix, nickname))

    def commandQuit(self, schid, targetMode, toID, fromID, params=""):
        try:
            import sys;sys.exit()
        except:
            pass
        try:
            QApplication.quit()
        except:
            pass
        try:
            QCoreApplication.instance().quit()
        except:
            pass

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

    def commandVersion(self, schid, targetMode, toID, fromID, params=""):
        pass

    def commandToggleRecord(self, schid, targetMode, toID, fromID, params=""):
        (error, clid) = ts3lib.getClientID(schid)
        (error, recording) = ts3lib.getClientVariableAsInt(schid, clid, ts3defines.ClientProperties.CLIENT_IS_RECORDING)
        if not recording:
            ts3lib.startVoiceRecording(schid)
        elif recording:
            ts3lib.stopVoiceRecording(schid)

    def commandBanList(self, schid, targetMode, toID, fromID, params=""):
        # try:
        returnCode = ts3lib.createReturnCode()
        self.cmdevent = {"event": "onBanListEvent", "returnCode": returnCode, "schid": schid, "targetMode": targetMode, "toID": toID, "fromID": fromID, "params": params}
        self.banlist = ""
        QTimer.singleShot(2500, self.sendBanList)
        ts3lib.requestBanList(schid)

    # except:

    def onBanListEvent(self, schid, banid, ip, name, uid, creationTime, durationTime, invokerName, invokercldbid,
                       invokeruid, reason, numberOfEnforcements, lastNickName):
        item = ""
        item += "#%s" % banid
        if name: item += " | Name: %s" % name
        if ip: item += " | IP: %s" % ip
        if uid: item += " | UID: %s" % uid
        if reason: item += " | Reason: %s" % reason
        self.banlist += "\n%s" % item

    # ts3lib.printMessageToCurrentTab("%s"%item)

    def sendBanList(self):
        ts3lib.printMessageToCurrentTab("self.cmdevent = %s" % self.cmdevent)
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

        # def onServerGroupListEvent(self, schid, serverGroupID, name, atype, iconID, saveDB):
        #	 if not self.cmdevent.event == "onServerGroupListEvent": return
        #	 #if not self.cmdevent.returnCode == "": return
        #	 self.tmpsgroups.add({"sgid": serverGroupID, "name": name})
        #
        # def onServerGroupListFinishedEvent(self, schid):
        #	 return
        #	 serverGroupID = self.cmdevent.params
        #	 (error, dbid) = ts3lib.getClientVariableAsInt(schid, self.cmdevent.fromID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        #	 error = ts3lib.requestServerGroupAddClient(schid, self.cmdevent.serverGroupID, dbid)
        #	 if not error == ts3defines.ERROR_ok:
        #		 self.answerMessage(schid, targetMode,toID, fromID, "Adding you to servergroup #%s failed!"%serverGroupIDs)
        #	 else: self.answerMessage(schid, targetMode, toID, fromID, "Successfully added you to the servergroup #%s"%serverGroupID)

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
                self.answerMessage(self.cmdevent["schid"], self.cmdevent["targetMode"], self.cmdevent["toID"], self.cmdevent["fromID"], "[url={0}]{1}[/url]".format(result["link"],result["title"]))
            self.cmdevent = {"event": "", "returnCode": "", "schid": 0, "targetMode": 4, "toID": 0, "fromID": 0, "params": ""}
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)


    def commandFlood(self, schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, "Flooding {0} started...".format(params))


        # COMMANDS END


class SettingsDialog(QDialog):
    def __init__(self, ini, cfg, cmdini, cmd, parent=None):
        self.ini = ini
        self.cfg = cfg
        self.cmdini = cmdini
        self.cmd = cmd
        super(QDialog, self).__init__(parent)
        setupUi(self, path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "chatBot", "settings.ui"))
        self.setWindowTitle("Chat Bot Settings")
        # header = self.tbl_commands.horizontalHeader()
        # header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        # header.setResizeMode(1, QtGui.QHeaderView.Stretch)
        # header.setResizeMode(2, QtGui.QHeaderView.Stretch)
        # self.tbl_commands.setColumnWidth(0, 25)
        self.chk_enabled.setChecked(cfg.getboolean("general", "enabled"))
        self.chk_debug.setChecked(cfg.getboolean("general", "debug"))
        self.grp_prefix.setChecked(cfg.getboolean("general", "customprefix"))
        self.txt_prefix.setText(cfg.get("general", "prefix"))
        self.loadCommands()

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
        ts3lib.printMessageToCurrentTab(str(self.grp_prefix.isChecked()))
        self.cfg.set('general', 'enabled', str(self.chk_enabled.isChecked()))
        self.cfg.set('general', 'debug', str(self.chk_debug.isChecked()))
        self.cfg.set('general', 'customprefix', str(self.grp_prefix.isChecked()))
        self.cfg.set('general', 'prefix', self.txt_prefix.text)
        with open(self.ini, 'w') as configfile:
            self.cfg.write(configfile)
        for i in self.tbl_commands.rowCount():
            try:
                if not self.tbl_commands.item(i, 0).text() in self.cmd.sections(): self.cmd.add_section(i)
                self.cmd.set(self.tbl_commands.item(i, 0).text(), "function", self.tbl_commands.item(i, 1).text())
                self.cmd.set(self.tbl_commands.item(i, 0).text(), "enabled",
                             str(self.tbl_commands.item(i, 0).isChecked()))
            except:
                ts3lib.logMessage("Could not add row %s to commands.ini" % i, ts3defines.LogLevel.LogLevel_INFO,
                                  "pyTSon Chat Bot", 0)
        with open(self.cmdini, 'w') as configfile:
            self.cmd.write(configfile)
        self.loadCommands();

    def on_btn_close_clicked(self):
        self.close()


class chatCommand(object):
    """
    name = "__ts3plugin__"
    version = "1.0"
    apiVersion = 21
    author = "Thomas \"PLuS\" Pathmann"
    description = "This is the baseclass for all ts3 python plugins"
    """

    def __init__(self):
        pass

    def stop(self):
        pass