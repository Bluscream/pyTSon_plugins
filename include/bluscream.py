#!/usr/bin/env python
# -*- coding: utf-8 -*-
#region imports
from datetime import datetime
from PythonQt import BoolResult
from PythonQt.Qt import QApplication
from PythonQt.QtGui import QInputDialog, QMessageBox, QWidget, QLineEdit #, QObject
from PythonQt.QtCore import Qt, QFile, QByteArray, QIODevice, QDataStream, QUrl # , QApplication # QDir
from PythonQt.QtSql import QSqlQuery
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from ts3plugin import PluginHost
# from configparser import ConfigParser
from urllib.parse import quote_plus
from gc import get_objects
from base64 import b64encode
from pytson import getPluginPath
from re import match, sub, compile, escape, search, IGNORECASE, MULTILINE
try:
    from psutil import Process
except ImportError:
    from devtools import PluginInstaller
    PluginInstaller().installPackages(['psutil'])
    from psutil import Process
import ts3lib, ts3defines, os.path, string, random, ts3client, time, sys, codecs
from ts3enums import *
#endregion
#region GENERAL FUNCTIONS
def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())
def date(): return '{:%Y-%m-%d}'.format(datetime.now())
def Time(): return '{:%H:%M:%S}'.format(datetime.now())
def getScriptPath(name): return getPluginPath("scripts", name) # TODO: use plugin.name

def boolean(_bool):
    if _bool and _bool.lower() == "true": return True
    elif _bool and _bool.lower() == "false": return False
    else: return None

def sanitize(s,hard=False):
    if hard: return sub('[^a-zA-Z]', '', s)
    return "".join(i for i in s if ord(i)<128)

class EncodedOut:
    def __init__(self, enc):
        self.enc = enc
        self.stdout = sys.stdout
    def __enter__(self):
        if sys.stdout.encoding is None:
            w = codecs.getwriter(self.enc)
            sys.stdout = w(sys.stdout)
    def __exit__(self, exc_ty, exc_val, tb):
        sys.stdout = self.stdout

def log(message, channel=ts3defines.LogLevel.LogLevel_INFO, server=0):
    """
    :param message:
    :param channel:
    :param server:
    """
    message = str(message)
    _f = "{} ({}) ".format(Time(), channel)
    if server > 0:
        _f += "#"+str(server)+" "
    _f += "Console> "+message
    ts3lib.logMessage(message, channel, "pyTSon Console", server)
    ts3lib.printMessageToCurrentTab(_f)
    # if PluginHost.shell: PluginHost.shell.appendLine(_f)
    print(_f)

def toggle(boolean):
    """
    :param boolean:
    :return:
    """
    boolean = not boolean
    return boolean

def varname(obj, callingLocals=locals()):
    """
    :param obj:
    :param callingLocals:
    :return:
    """
    for k, v in list(callingLocals.items()):
         if v is obj: return k

def random_string(size=1, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    """
    :param size:
    :param chars:
    :return:
    """
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

def percentage(part, whole):
    """
    Returns rounded Percentage of <part> of <whole>
    :param part:
    :param whole:
    :return:
    """
    return round(100 * float(part)/float(whole))

def percent(percent, whole):
  """
  Returns rounded <percent>% of <whole>
  :param percent:
  :param whole:
  :return:
  """
  return round((percent * whole))

def intList(str, sep=","):
    """
    Returns a list of ints from a string
    :param str:
    :param sep:
    :return:
    """
    return [int(x) for x in str.split(sep)]

def getItem(useList, name): # getitem(PluginHost.modules,'devTools')
    """
    :param useList:
    :param name:
    :return:
    """
    for _name,value in useList.items():
        if _name == name: return value

def getItems(object):
    """
    :param object:
    :return:
    """
    return [(a, getattr(object, a)) for a in dir(object)
            if not a.startswith('__') and not callable(getattr(object, a)) and not "ENDMARKER" in a and not "DUMMY" in a]

def getItemType(lst):
    """
    :param lst:
    :return:
    """
    if lst in [ts3defines.VirtualServerProperties, ts3defines.VirtualServerPropertiesRare]:
        return ts3defines.PluginItemType.PLUGIN_SERVER, "Server"
    elif lst in [ts3defines.ChannelProperties, ts3defines.ChannelPropertiesRare]:
        return ts3defines.PluginItemType.PLUGIN_CHANNEL, "Channel"
    elif lst in [ts3defines.ConnectionProperties, ts3defines.ConnectionPropertiesRare, ts3defines.ClientProperties, ts3defines.ClientPropertiesRare]:
        return ts3defines.PluginItemType.PLUGIN_CLIENT, "Client"
    else: return None

def find_between(s, first, last):
    """
    :param s:
    :param first:
    :param last:
    :return:
    """
    # type: (object, object, object) -> object
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_between_r(s, first, last):
    """
    :param s:
    :param first:
    :param last:
    :return:
    """
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def generateAvatarFileName(schid, clid=0):
    """
    :param schid:
    :param clid:
    :return:
    """
    if clid == 0: (error, clid) = ts3lib.getClientID(schid)
    (error, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
    return "avatar_"+b64encode(uid.encode('ascii')).decode("ascii").split('=')[0]
#endregion
#region PARSING
def serverURL(schid=None, name=None):
    if schid is None:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if name is None:
        try: (error, name) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
        except: name = schid
    return '[b][url=channelid://0]"{}"[/url][/b]'.format(name)

def channelURL(schid=None, cid=0, name=None):
    """
    :param schid:
    :param cid:
    :param name:
    :return:
    """
    if schid is None:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if name is None:
        try: (error, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
        except: name = cid
    return '[b][url=channelid://{0}]"{1}"[/url][/b]'.format(cid, name)

# pattern_channelurl = compile("^\[URL=channelid:\/\/(\d+)\](.*)\[\/URL\]$")
def parseChannelURL(url):
    pattern = "^\[URL=channelid:\/\/(\d+)\](.*)\[\/URL\]$"
    regex = search(pattern, url, IGNORECASE)
    if regex:
        cid = regex.group(1)
        name = regex.group(2)
        return cid, name
    return False

def clientURL(schid=0, clid=0, uid="", nickname="", nickname_encoded=""):
    """
    :param schid:
    :param clid:
    :param uid:
    :param nickname:
    :param nickname_encoded:
    :return:
    """
    if not schid:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if not uid:
        try: (error, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        except: pass
    if not nickname:
        try: (error, nickname) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        except: nickname = uid
    if not nickname_encoded:
        try: nickname_encoded = quote_plus(nickname)
        except: nickname_encoded = uid
    return '[url=client://{0}/{1}~{2}]"{3}"[/url]'.format(clid, uid, nickname_encoded, nickname)

def parseClientURL(url):
    pattern = "^\[URL=client:\/\/(\d+)\/(.*)~(.*)\](.*)\[\/URL\]$"
    regex = search(pattern, url, IGNORECASE)
    if regex:
        clid = regex.group(1)
        uid = regex.group(2)
        nickname_encoded = regex.group(3)
        nickname = regex.group(4)
        return clid, uid, nickname_encoded, nickname
    return False

def getChannelPassword(schid, cid, crack=False, ask=False):
    """
    Tries several methods to get the channel password.
    :param schid: serverConnectionHandlerID
    :param cid: channelID of the target channel
    :param crack: wether to try a dictionary attack on the channel to get the password
    :param ask: wether to ask the user for the password in case he knows
    :return password: the possible password
    """
    # type: (int, int, bool, bool) -> str
    (err, passworded) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
    if err != ts3defines.ERROR_ok or not passworded: return False
    (err, path, pw) = ts3lib.getChannelConnectInfo(schid, cid)
    if pw: return pw
    (err, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
    if err != ts3defines.ERROR_ok or not name: return err
    name = name.strip()
    pattern = r"(?:pw|pass(?:wor[dt])?)[|:=]?\s*(.*)"
    # pattern = r"^.*[kennwort|pw|password|passwort|pass|passwd](.*)$"
    regex = search(pattern, name, IGNORECASE)
    if regex:
        result = regex.group(1).strip()
        result = sub(r"[)|\]|\}]$", "", result)
        return result
    if name.isdigit(): return name
    if crack:
        active = PluginHost.active
        if "PW Cracker" in active: active["PW Cracker"].onMenuItemEvent(schid, ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 1, cid)
    if ask:
        pw = inputBox("Enter Channel Password", "Password:", name)
        return pw
    return name

def getClientIDByUID(schid, uid):
    (err, clids) = ts3lib.getClientList(schid)
    for clid in clids:
        (err, _uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if uid == _uid: return clid
    return False

def getServerType(schid, pattern=None):
    err, ver = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_VERSION)
    if err != ts3defines.ERROR_ok or not ver: return ServerInstanceType.UNKNOWN
    err, platform = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_PLATFORM)
    if err != ts3defines.ERROR_ok or not platform: return ServerInstanceType.UNKNOWN
    valid_platform = platform in ["Windows", "Linux", "OS X", "FreeBSD"]
    if pattern is not None: valid_version = pattern.match(ver)
    else: valid_version = match('3(?:\.\d+)* \[Build: \d+\]', ver)
    if valid_version and valid_platform: return ServerInstanceType.VANILLA
    elif "teaspeak" in ver.lower(): return ServerInstanceType.TEASPEAK
    else: return ServerInstanceType.UNKNOWN

def parseTime(time_str):
    return datetime.strptime(time_str.rsplit('.', 1)[0], "%Y-%m-%d %H:%M:%S") # 2017-05-31 21:51:28.563532

def getClientIDByName(name:str, schid:int=0, use_displayname:bool=False, multi:bool=False):
    if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
    if multi: results = []
    (err, clids) = ts3lib.getClientList(schid)
    for clid in clids:
        if use_displayname:(err, _name) = ts3lib.getClientDisplayName(schid, clid)
        else: (err, _name) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if name == _name:
            if multi: results.append(clid)
            else: return clid
    if multi and len(results): return results

def getChannelIDByName(name:str, schid:int=0, multi:bool=False):
    if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
    if multi: results = []
    (err, cids) = ts3lib.getChannelList(schid)
    for cid in cids:
        (err, _name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
        if name == _name:
            if multi: results.append(cid)
            else: return cid
    if multi and len(results): return results

def getIDByName(name:str, schid:int=0):
    if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
    err, sname = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)
    if sname == name: return 0, ServerTreeItemType.SERVER
    cid = getChannelIDByName(name, schid)
    if cid: return cid, ServerTreeItemType.CHANNEL
    clid = getClientIDByName(name, schid, use_displayname=True)
    if clid: return clid, ServerTreeItemType.CLIENT
    return 0, ServerTreeItemType.UNKNOWN
#endregion
#region AntiFlood
def getAntiFloodSettings(schid):
    """
    :param schid:
    :return:
    """
    (err, cmdblock) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ANTIFLOOD_POINTS_NEEDED_COMMAND_BLOCK)
    (err, ipblock) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ANTIFLOOD_POINTS_NEEDED_IP_BLOCK)
    (err, afreduce) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ANTIFLOOD_POINTS_TICK_REDUCE)
    return err, cmdblock, ipblock, afreduce

def calculateInterval(schid, command, name="pyTSon"):
    """
    :param schid:
    :param command:
    :param name:
    :return: interval: int
    """
    # ts3lib.requestServerVariables(schid)
    (err, cmdblock, ipblock, afreduce) = getAntiFloodSettings(schid)
    # strange = False
    # for var in [cmdblock, ipblock, afreduce]:
        # if not var or var < 0 or var == "": strange = True
    # if err != ts3defines.ERROR_ok or strange:
        # ts3lib.requestServerVariables(schid)
        # (err, cmdblock, ipblock, afreduce) = getAntiFloodSettings(schid)
    interval = round(1000/(afreduce/command))
    ts3lib.logMessage("{}: schid = {} | err = {} | afreduce = {} | cmdblock = {} | ipblock = {} | points_per_{} = {} |interval = {}".format(name, schid, err, afreduce, cmdblock, ipblock, varname(command, locals()), command, interval), ts3defines.LogLevel.LogLevel_INFO, "pyTSon", 0)
    return interval
#endregion
#region I/O
def loadCfg(path, cfg):
    """
    :param path:
    :param cfg:
    """
    if not os.path.isfile(path) or os.path.getsize(path) < 1:
        saveCfg(path, cfg)
    cfg = cfg.read(path, encoding='utf-8')

def saveCfg(path, cfg):
    """
    :param path:
    :param cfg:
    """
    with open(path, mode='w', encoding="utf-8") as cfgfile:
        cfg.write(cfgfile)
#endregion
#region GUI
def inputBox(title, text, default=""):
    """
    :param default:
    :param title:
    :param text:
    :return:
    """
    x = QWidget()
    x.setAttribute(Qt.WA_DeleteOnClose)
    ok = BoolResult()
    if not default: default = QApplication.clipboard().text()
    text = QInputDialog.getText(x, title, text, QLineEdit.Normal, default, ok) # QDir.Home.dirName()
    if ok: return text
    else: return False

def inputInt(title="", label="", val=0, min=-2147483647, max=2147483647, step=1):
    """
    :param title:
    :param label:
    :param val:
    :param min:
    :param max:
    :param step:
    :return:
    """
    x = QWidget()
    x.setAttribute(Qt.WA_DeleteOnClose)
    ok = BoolResult()
    i = QInputDialog.getInt(x, title, label, val, min, max, step, ok)
    if ok: return i
    else: return False

def msgBox(text, icon=QMessageBox.Information, title=""):
    """
    :param text:
    :param icon:
    :param title:
    """
    x = QMessageBox()
    if title: x.setWindowTitle(title)
    x.setText(text)
    x.setIcon(icon)
    x.exec()

def errorMsgBox(title, text):
    QMessageBox.critical(None, title, text)

def confirm(title, message):
    """
    :param title:
    :param message:
    :return:
    """
    x = QWidget()
    x.setAttribute(Qt.WA_DeleteOnClose)
    _x = QMessageBox.question(x, title, message, QMessageBox.Yes, QMessageBox.No)
    if _x == QMessageBox.Yes: return True if _x == QMessageBox.Yes else False

def getobjects(name, cls=True):
    """
    :param name:
    :param cls:
    :return:
    """
    objects = []
    for obj in get_objects():
        if (isinstance(obj, QObject) and
                ((cls and obj.inherits(name)) or
                 (not cls and obj.objectName() == name))):
            objects.append(obj)
    return objects
#endregion
#region QT Manipulation
def objects():
    """
    :return:
    """
    _ret = []
    for x in get_objects(): _ret.extend(str(repr(x)))
    return _ret

def grabWidget(objName, byClass=False):
    for widget in QApplication.instance().allWidgets():
        try:
            if byClass and widget.className() == objName: return widget
            elif widget.objectName == objName: return widget
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

def findWidget(name):
    try:
        name = name.lower()
        instance = QApplication.instance()
        widgets = instance.topLevelWidgets()
        widgets = widgets + instance.allWidgets()
        ret = dict()
        c = 0
        for x in widgets:
            c += 1
            if name in x.objectName.lower() or name in str(x.__class__).lower():
                ret["class:"+str(x.__class__)+str(c)] = "obj:"+x.objectName;continue
            if hasattr(x, "text"):
                if name in x.text.lower():
                    ret["class:"+str(x.__class__)+str(c)] = "obj:"+x.objectName
        return ret
    except:
        print("error")
def widgetbyclass(name):
    ret = []
    instance = QApplication.instance()
    widgets = instance.topLevelWidgets()
    widgets = widgets + instance.allWidgets()
    for x in widgets:
        if name in str(x.__class__).replace("<class '","").replace("'>",""):
            ret.extend(x)
    return ret
def widgetbyobject(name):
    name = name.lower()
    instance = QApplication.instance()
    widgets = instance.topLevelWidgets()
    widgets = widgets + instance.allWidgets()
    for x in widgets:
        if str(x.objectName).lower() == name:
            return x
#endregion
#region Network
class network(object):
    nwmc = QNetworkAccessManager()
    def getFile(self, url):
        """
        :param url:
        """
        self.nwmc.connect("finished(QNetworkReply*)", self._getFileReply)
        self.nwmc.get(QNetworkRequest(QUrl(url)))
    def _getFileReply(self, reply):
        del self.nwmc

    def downloadFile(self, url, path):
        """
        :param url:
        :param path:
        """
        self.nwmc.connect("finished(QNetworkReply*)", self._downloadFileReply)
        dlpath = path
        self.nwmc.get(QNetworkRequest(QUrl(url)))
    def _downloadFileReply(self, reply):
        del self.nwmc
        """
        QByteArray b = reply->readAll();
        fil = QFile(dlpath);
        fil.open(QIODevice.WriteOnly);
        out QDataStream(fil);
        out << b;
        """
#endregion
#region Stuff
def getAddonStatus(filename_without_extension="", name=""): # getAddonStatus("TS3Hook", "TS3Hook") getAddonStatus("tspatch", "TS Patch")
    """
    :param filename_without_extension:
    :param name:
    :return: AddonStatus
    """
    to_remove = ('_win64', '_win32', '_x64', '_x86')
    r = compile(r'({})\.dll$'.format('|'.join(map(escape, to_remove))), flags=IGNORECASE)
    if filename_without_extension:
        p = Process(os.getpid())
        filename = filename_without_extension.lower()
        # pattern = compile("^(?:.*)(_win64|_win32|_x64|_x86)?\.dll$", IGNORECASE|MULTILINE)
        for dll in p.memory_maps():
            # file = dll.path.lower().rsplit('\\', 1)[1].replace("_win64","").replace("_win32","").replace("_x86","").replace("_x64","").replace(".DLL","").replace(".dll","")
            file = dll.path.lower()
            if not file.endswith(".dll") and not file.endswith(".so"): continue
            file = r.sub(r'', dll.path).lower().rstrip('.dll')
            if file.endswith(filename): return AddonStatus.LOADED #, ExtendedAddonStatus.MEMORY # pattern.sub("", file)
    if name:
        addons = getAddons()
        for k in addons:
            if addons[k]["name"] == name: return AddonStatus.INSTALLED #, ExtendedAddonStatus.DATABASE
    if filename_without_extension:
        for filename in os.listdir(ts3lib.getPluginPath()):
            filename = r.sub(r'', filename).lower().rstrip('.dll')
            if filename == filename_without_extension:
                return  AddonStatus.INSTALLED #, ExtendedAddonStatus.FOLDER
    return AddonStatus.UNKNOWN #, ExtendedAddonStatus.UNKNOWN
#endregion
#region Database
def getAddons():
    """
    :return:
    """
    db = ts3client.Config()
    q = db.query("SELECT * FROM addons")
    ret = {}
    while q.next():
        try:
            key = q.value("key")
            ret[key] = {"timestamp": q.value("timestamp")}
            val = q.value("value")
            for l in val.split('\n'):
                l = l.split('=', 1)
                ret[key][l[0]] = l[1]
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0);continue
    return ret

def getContacts():
    """
    :return:
    """
    db = ts3client.Config()
    ret = []
    q = db.query("SELECT * FROM contacts")
    while q.next():
        try:
            cur = {"Key": int(q.value("key")), "Timestamp": q.value("timestamp")}
            val = q.value("value")
            for l in val.split('\n'):
                try:
                    l = l.split('=', 1)
                    if len(l) != 2: continue
                    if l[0] in ["Nickname","PhoneticNickname","LastSeenServerName"]: cur[l[0]] = l[1].encode('ascii', 'ignore')
                    elif l[0] in ["LastSeenServerAddress","IDS","VolumeModifier", "LastSeen"]: cur[l[0]] = l[1]
                    elif l[0] in ["Friend","NickShowType"]: cur[l[0]] = int(l[1])
                    elif l[0] in ["Automute","IgnorePublicMessages","IgnorePrivateMessages","IgnorePokes","IgnoreAvatar","IgnoreAwayMessage","HaveVolumeModifier","WhisperAllow"]:
                        if l[1] == "false": cur[l[0]] = False
                        elif l[1] == "true": cur[l[0]] = True
                    if l[0] == "LastSeen" and l[1]: cur["LastSeenEpoch"] = int(time.mktime(time.strptime(l[1], '%Y-%m-%dT%H:%M:%S')))
                except: continue
            ret.append(cur)
        except: continue
    del db
    return ret

def getContactStatus(uid):
    """
    :param uid:
    :return:
    """
    db = ts3client.Config()
    q = db.query("SELECT * FROM contacts WHERE value LIKE '%%IDS=%s%%'" % uid)
    ret = 2
    if q.next():
        val = q.value("value")
        for l in val.split('\n'):
            if l.startswith('Friend='):
                ret = int(l[-1])
    del db
    return ret
#endregion
#region TS3Hook
def escapeStr(str,unescape=False):
    """
    :param str:
    :param unescape:
    :return:
    """
    if unescape: return str.replace(" ","\s").replace("|","\p").replace("    ","\t")
    return str.replace("\s"," ").replace("\p","|").replace("\t","    ")

def parseCommand(cmd):
    """

    :param cmd:
    :return:
    """
    _cmd = cmd.split(' ', 1)
    cmd = _cmd[0]
    params = {}
    if len(_cmd) > 1:
        _params = _cmd[1].split(' ')
        for param in _params:
            param = param.split('=', 1)
            params[param[0]] = escapeStr(param[1]) if len(param) > 1 else None
    return cmd, params

def buildCommand(cmd, parameters):
    """

    :param cmd:
    :param parameters:
    :return:
    """
    for key, value in parameters:
        if key.startswith('-') or not value:
            cmd += " {}".format(key)
        else: cmd += " {}={}".format(key[0], key[1])
    return cmd


def parseBadgesBlob(blob: QByteArray):
    ret = {}
    next = 12
    guid_len = 0;guid = ""
    name_len = 0;name = ""
    url_len = 0;url = ""
    filename = ""
    desc_len = 0;desc = ""
    for i in range(0, blob.size()):
        try:
            if i == next: #guid_len
                guid_len = int(blob.at(i))
                guid = str(blob.mid(i+1, guid_len))
            elif i == (next + 1 + guid_len + 1):
                name_len = int(blob.at(i))
                name = str(blob.mid(i+1, name_len))
            elif i == (next + 1 + guid_len + 1 + name_len + 2):
                url_len = int(blob.at(i))
                url = str(blob.mid(i+1, url_len))
                filename = url.rsplit('/', 1)[1]
            elif i == (next + 1 + guid_len + 1 + name_len + 2 + url_len + 2):
                desc_len = int(blob.at(i))
                desc = str(blob.mid(i+1, desc_len))
                ret[guid] = {"name": name, "url": url, "filename": filename, "description": desc}
                next = (next + guid_len + 2 + name_len + 2 + url_len + 2 + desc_len + 13)
            delimiter = blob.mid(0, 12)
        except:
            from traceback import format_exc; ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
            pass
    return ret, blob


def loadBadges():
    """
    Loads Badges from ts3settings.db
    :return: int(timestamp), str(ret), dict(badges)
    """
    db = ts3client.Config()
    q = db.query("SELECT * FROM Badges") #  WHERE key = BadgesListData
    timestamp = 0
    ret = {}
    badges = QByteArray()
    while q.next():
        key = q.value("key")
        if key == "BadgesListTimestamp":
            timestamp = q.value("value")
        elif key == "BadgesListData":
            ret, badges = parseBadgesBlob(q.value("value"))
    del db
    return timestamp, ret, badges

def parseBadges(client_badges):
    """
    Parses a string of badges.
    :param client_badges:
    :return: tuple(overwolf, dict(badges))
    """
    overwolf = None
    badges = []
    if "verwolf=" in client_badges and "badges=" in client_badges:
        client_badges = client_badges.split(":",1)
        overwolf = bool(int(client_badges[0].split("=",1)[1]))
        badges = client_badges[1].split("=",1)[1].replace(":badges=", ",").split(",")
    elif "verwolf=" in client_badges:
        overwolf = bool(int(client_badges.split("=")[1]))
    elif "badges=" in client_badges:
        badges = client_badges.split("=",1)[1].replace(":badges=", ",").split(",")
    return overwolf, badges

def buildBadges(badges=[], overwolf=False):
    """
    Builds a badges command from a list of badges.
    :param badges:
    :param overwolf:
    :return: str(clientupdate cmd with badges)
    """
    blocks = [",".join(badges[i:i+3]) for i in range(0, len(badges), 3)]
    return "clientupdate client_badges=overwolf={}:badges={}".format(1 if overwolf else 0, ":badges=".join(blocks))

def sendCommand(name, cmd, schid=0, silent=True, reverse=False, mode=1):
    """
    Sends a command through TS3Hook.
    :param mode: See enum: HookMode
    :param reverse:
    :param name:
    :param cmd:
    :param schid:
    :param silent:
    """
    if schid == 0: schid = ts3lib.getCurrentServerConnectionHandlerID()
    if PluginHost.cfg.getboolean("general", "verbose") or not silent:
        ts3lib.printMessage(schid, '{timestamp} [color=orange]{name}[/color]:[color=white] {prefix}{message}'.format(timestamp=timestamp(), name=name, prefix="-" if reverse else "~", message=cmd), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
    print("mode:",mode)
    if mode == HookMode.TS3HOOK:
        cmd = "{}cmd{}".format("-" if reverse else "~", cmd.replace(" ", "~s"))
    elif mode == HookMode.TSPATCH:
        cmd = "{}{}".format("-" if reverse else "~", cmd)
    else: raise SyntaxError("No HookMode specified!")
    (err, clid) = ts3lib.getClientID(schid)
    retcode = "" # "TS3Hook:Command:{}".format(ts3lib.createReturnCode(256))
    err = ts3lib.requestSendPrivateTextMsg(schid, cmd, clid, retcode)
    if err != ts3defines.ERROR_ok: ts3lib.requestSendChannelTextMsg(schid, cmd, 0, retcode)
    if err != ts3defines.ERROR_ok: ts3lib.requestSendServerTextMsg(schid, cmd, retcode)
#endregion
#region DEFINES
dlpath = ""

class HookMode(Enum):
    NONE = 0
    TS3HOOK = 1
    TSPATCH = 2
#endregion
"""
    def log(self, logLevel, message, schid=0):
        ts3lib.logMessage(message, logLevel, self.name, schid)
        if logLevel in [ts3defines.LogLevel.LogLevel_DEBUG, ts3defines.LogLevel.LogLevel_DEVEL] and self.debug:
            ts3lib.printMessage(schid if schid else ts3lib.getCurrentServerConnectionHandlerID(), '{timestamp} [color=orange]{name}[/color]: {message}'.format(timestamp=self.timestamp(), name=self.name, message=message), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)

"""
"""
with EncodedOut('utf-8'):
    print("Loaded", __file__)
"""