from datetime import datetime
from PythonQt.QtGui import QInputDialog, QMessageBox, QDialog
from PythonQt.QtCore import Qt, QFile, QByteArray, QIODevice, QDataStream, QSqlQuery
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from ts3plugin import PluginHost
# from configparser import ConfigParser
import ts3lib, ts3defines, os.path, string, random, ts3client

# GENERAL FUNCTIONS #
def timestamp():
    return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

def varname(obj, callingLocals=locals()):
    for k, v in list(callingLocals.items()):
         if v is obj: return k

def random_string(size=1, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

# PARSING #
def channelURL(schid=None, cid=0, name=None):
    if schid == None:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if name == None:
        try: (error, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
        except: name = cid
    return '[b][url=channelid://{0}]"{1}"[/url][/b]'.format(cid, name)

def clientURL(schid=None, clid=0, uid=None, nickname=None):
    if schid == None:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if uid == None:
        try: (error, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        except: pass
    if nickname == None:
        try: (error, nickname) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        except: nickname = uid
    return '[url=client://{0}/{1}]{2}[/url]'.format(clid, uid, nickname)

# I/O #
def loadCfg(path, cfg):
    if not os.path.isfile(path) or os.path.getsize(path) < 1:
        saveCfg(path, cfg)
    cfg = cfg.read(path)

def saveCfg(path, cfg):
    with open(path, 'w') as cfgfile:
        cfg.write(cfgfile)
# GUI #
def inputBox(title, text):
    x = QDialog()
    x.setAttribute(Qt.WA_DeleteOnClose)
    return QInputDialog.getText(x, title, text)

def msgBox(text, icon=QMessageBox.Information):
    x = QMessageBox()
    x.setText(text)
    x.setIcon(icon)
    x.exec()

def confirm(title, message):
    x = QDialog()
    x.setAttribute(Qt.WA_DeleteOnClose)
    _x = QMessageBox.question(x, title, message, QMessageBox.Yes, QMessageBox.No)
    if _x == QMessageBox.Yes: return True if _x == QMessageBox.Yes else False

# AntiFlood
def getAntiFloodSettings(schid):
    (err, cmdblock) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ANTIFLOOD_POINTS_NEEDED_COMMAND_BLOCK)
    (err, ipblock) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ANTIFLOOD_POINTS_NEEDED_IP_BLOCK)
    (err, afreduce) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ANTIFLOOD_POINTS_TICK_REDUCE)
    return (err, cmdblock, ipblock, afreduce)

def calculateInterval(schid, command, name="pyTSon"):
    # ts3lib.requestServerVariables(schid)
    (err, cmdblock, ipblock, afreduce) = getAntiFloodSettings(schid)
    # strange = False
    # for var in [cmdblock, ipblock, afreduce]:
        # if not var or var < 0 or var == "": strange = True
    # if err != ts3defines.ERROR_ok or strange:
        # ts3lib.requestServerVariables(schid)
        # (err, cmdblock, ipblock, afreduce) = getAntiFloodSettings(schid)
    interval = round(1000/((afreduce/command)))
    ts3lib.logMessage("{}: schid = {} | err = {} | afreduce = {} | cmdblock = {} | ipblock = {} | points_per_{} = {} |interval = {}".format(name, schid, err, afreduce, cmdblock, ipblock, varname(command), command, interval), ts3defines.LogLevel.LogLevel_INFO, "pyTSon", 0)
    return interval

# Network #
def getFile(url):
    nwmc = QNetworkAccessManager()
    nwmc.connect("finished(QNetworkReply*)", getFile)
    nwmc.get(QNetworkRequest(QUrl(url)))
def getFileReply(reply):
    del nwmc


def downloadFile(url, path):
    nwmc = QNetworkAccessManager()
    nwmc.connect("finished(QNetworkReply*)", downloadFileReply)
    dlpath = path
    nwmc.get(QNetworkRequest(QUrl(url)))
def downloadFileReply(reply):
    del nwmc
    """
    QByteArray b = reply->readAll();
    fil = QFile(dlpath);
    fil.open(QIODevice.WriteOnly);
    out QDataStream(fil);
    out << b;
    """

# TS3Hook #
def parseCommand(cmd):
    pass

def buildCommand(cmd, parameters):
    for key, value in parameters:
        if key.startswith('-') or not value:
            cmd += " {}".format(key)
        else: cmd += " {}={}".format(key[0], key[1])
    return cmd

def saveBadges(external):
    db = ts3client.Config()
    query = QSqlQuery(db)
    (timestamp, official, array) = loadBadges()
    delimiter = array.mid(0, 12)
    delimiter1 = 0;delimiter2 = 0;delimiter3 = 0;delimiter4 = 0
    guid_len = 0;guid = ""
    name_len = 0;name = ""
    url_len = 0;url = ""
    desc_len = 0;desc = ""
    for i in range(0, array.size()):
        if i == 12: #guid_len
            guid_len = int(array.at(i))
            guid = str(array.mid(i+1, guid_len))
        elif i == (12 + 1 + guid_len + 1):
            delimiter1 = array.mid(i - 1)
            name_len = int(array.at(i))
            name = str(array.mid(i+1, name_len))
        elif i == (12 + 1 + guid_len + 1 + name_len + 2):
            delimiter2 = array.mid(i - 1)
            url_len = int(array.at(i))
            url = str(array.mid(i+1, url_len))
        elif i == (12 + 1 + guid_len + 1 + name_len + 2 + url_len + 2):
            delimiter3 = array.mid(i - 3)
            desc_len = int(array.at(i))
            desc = str(array.mid(i+1, desc_len))
            break
    print(delimiter)
    print(delimiter1)
    print(delimiter2)
    print(delimiter3)
    print(delimiter4)
    print(array)
    # query.prepare( "UPDATE Badges (BadgesListData) VALUES (:byteArray)" );
    # query.bindValue( ":imageData", array);


def loadBadges():
    db = ts3client.Config()
    q = db.query("SELECT * FROM Badges") #  WHERE key = BadgesListData
    timestamp = 0
    ret = {}
    badges = b''
    while q.next():
        key = q.value("key")
        if key == "BadgesListTimestamp":
            timestamp = q.value("value")
        elif key == "BadgesListData":
            badges = q.value("value")
            next = 12
            guid_len = 0;guid = ""
            name_len = 0;name = ""
            url_len = 0;url = ""
            filename = ""
            desc_len = 0;desc = ""
            try:
                for i in range(0, badges.size()):
                    if i == next: #guid_len
                        guid_len = int(badges.at(i))
                        guid = str(badges.mid(i+1, guid_len))
                    elif i == (next + 1 + guid_len + 1):
                        name_len = int(badges.at(i))
                        name = str(badges.mid(i+1, name_len))
                    elif i == (next + 1 + guid_len + 1 + name_len + 2):
                        url_len = int(badges.at(i))
                        url = str(badges.mid(i+1, url_len))
                        filename = url.rsplit('/', 1)[1]
                    elif i == (next + 1 + guid_len + 1 + name_len + 2 + url_len + 2):
                        desc_len = int(badges.at(i))
                        desc = str(badges.mid(i+1, desc_len))
                        ret[guid] = {"name": name, "url": url, "filename": filename, "description": desc}
                        next = (next + guid_len + 2 + name_len + 2 + url_len + 2 + desc_len + 13)
                delimiter = badges.mid(0, 12)
            except: from traceback import format_exc; ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
    del db
    return timestamp, ret, badges

def parseBadges(client_badges):
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
    return (overwolf, badges)

def buildBadges(badges=[], overwolf=False):
    blocks = [",".join(badges[i:i+3]) for i in range(0, len(badges), 3)]
    return "clientupdate client_badges=overwolf={}:badges={}".format(1 if overwolf else 0, ":badges=".join(blocks))

def sendCommand(name, cmd, schid=0):
    if PluginHost.cfg.getboolean("general", "verbose"):
        ts3lib.printMessage(ts3lib.getCurrentServerConnectionHandlerID(), '{timestamp} [color=orange]{name}[/color]:[color=white] {message}'.format(timestamp=timestamp(), name=name, message=cmd), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
    cmd = cmd.replace(" ", "~s")
    if schid == 0: schid = ts3lib.getCurrentServerConnectionHandlerID()
    ts3lib.requestSendServerTextMsg(schid, "~cmd{}".format(cmd))

# DEFINES #

dlpath = ""

class AntiFloodPoints(object):
    AUTH = 0
    BANADD = 25
    BANCLIENT = 25
    BANDEL = 5
    BANDELALL = 5
    BANLIST = 25
    BINDINGLIST = 0
    CHANNELADDPERM = 5
    CHANNELCLIENTADDPERM = 5
    CHANNELCLIENTDELPERM = 5
    CHANNELCLIENTLIST = 0
    CHANNELCLIENTPERMLIST = 5
    CHANNELCONNECTINFO = 0
    CHANNELCREATE = 25
    CHANNELCREATEPRIVATE = 25
    CHANNELDELETE = 25
    CHANNELDELPERM = 5
    CHANNELEDIT = 25
    CHANNELFIND = 0
    CHANNELGETDESCRIPTION = 0
    CHANNELGROUPADD = 5
    CHANNELGROUPADDPERM = 5
    CHANNELGROUPCLIENTLIST = 5
    CHANNELGROUPCOPY = 5
    CHANNELGROUPDEL = 5
    CHANNELGROUPDELPERM = 5
    CHANNELGROUPLIST = 5
    CHANNELGROUPPERMLIST = 5
    CHANNELGROUPRENAME = 5
    CHANNELINFO = 0
    CHANNELLIST = 0
    CHANNELMOVE = 25
    CHANNELPERMLIST = 5
    CHANNELSUBSCRIBE = 15
    CHANNELSUBSCRIBEALL = 20
    CHANNELUNSUBSCRIBE = 5
    CHANNELUNSUBSCRIBEALL = 25
    CHANNELVARIABLE = 0
    CLIENTADDPERM = 5
    CLIENTCHATCLOSED = 5
    CLIENTCHATCOMPOSING = 0
    CLIENTDBDELETE = 25
    CLIENTDBEDIT = 25
    CLIENTDBFIND = 50
    CLIENTDBINFO = 0
    CLIENTDBLIST = 25
    CLIENTDELPERM = 5
    CLIENTDISCONNECT = 0
    CLIENTEDIT = 25
    CLIENTFIND = 0
    CLIENTGETDBIDFROMUID = 5
    CLIENTGETIDS = 5
    CLIENTGETNAMEFROMDBID = 5
    CLIENTGETNAMEFROMUID = 5
    CLIENTGETUIDFROMCLID = 5
    CLIENTGETVARIABLES = 0
    CLIENTINFO = 0
    CLIENTINIT = 0
    CLIENTINITIV = 0
    CLIENTKICK = 25
    CLIENTLIST = 0
    CLIENTMOVE = 10
    CLIENTMUTE = 10
    CLIENTNOTIFYREGISTER = 0
    CLIENTNOTIFYUNREGISTER = 0
    CLIENTPERMLIST = 5
    CLIENTPOKE = 25
    CLIENTSETSERVERQUERYLOGIN = 25
    CLIENTSITEREPORT = 0
    CLIENTUNMUTE = 10
    CLIENTUPDATE = 15
    CLIENTVARIABLE = 0
    COMPLAINADD = 25
    COMPLAINDEL = 5
    COMPLAINDELALL = 25
    COMPLAINLIST = 25
    CONNECTIONINFOAUTOUPDATE = 0
    CURRENTSCHANDLERID = 0
    CUSTOMINFO = 0
    CUSTOMSEARCH = 50
    DUMMY_CONNECTFAILED = 0
    DUMMY_CONNECTIONLOST = 0
    DUMMY_NEWIP = 0
    FTCREATEDIR = 5
    FTDELETEFILE = 5
    FTGETFILEINFO = 5
    FTGETFILELIST = 0
    FTINITDOWNLOAD = 0
    FTINITUPLOAD = 0
    FTLIST = 5
    FTRENAMEFILE = 5
    FTSTOP = 5
    GETCONNECTIONINFO = 0
    GM = 50
    HASHPASSWORD = 0
    HELP = 0
    INSTANCEEDIT = 25
    INSTANCEINFO = 0
    LOGADD = 0
    LOGIN = 0
    LOGOUT = 0
    LOGVIEW = 50
    MESSAGEADD = 25
    MESSAGEDEL = 5
    MESSAGEGET = 20
    MESSAGELIST = 25
    MESSAGEUPDATEFLAG = 5
    PERMFIND = 0
    PERMGET = 0
    PERMIDGETBYNAME = 0
    PERMISSIONLIST = 5
    PERMOVERVIEW = 5
    PERMRESET = 0
    PLUGINCMD = 5
    PRIVILEGEKEYADD = 0
    PRIVILEGEKEYDELETE = 0
    PRIVILEGEKEYLIST = 0
    PRIVILEGEKEYUSE = 0
    QUIT = 0
    SERVERCONNECTINFO = 0
    SERVERCONNECTIONHANDLERLIST = 0
    SERVERCREATE = 0
    SERVERDELETE = 0
    SERVEREDIT = 5
    SERVERGETVARIABLES = 0
    SERVERGROUPADD = 5
    SERVERGROUPADDCLIENT = 25
    SERVERGROUPADDPERM = 5
    SERVERGROUPAUTOADDPERM = 0
    SERVERGROUPAUTODELPERM = 0
    SERVERGROUPCLIENTLIST = 5
    SERVERGROUPCOPY = 5
    SERVERGROUPDEL = 5
    SERVERGROUPDELCLIENT = 25
    SERVERGROUPDELPERM = 5
    SERVERGROUPLIST = 5
    SERVERGROUPPERMLIST = 5
    SERVERGROUPRENAME = 5
    SERVERGROUPSBYCLIENTID = 5
    SERVERIDGETBYPORT = 0
    SERVERINFO = 0
    SERVERLIST = 0
    SERVERNOTIFYREGISTER = 0
    SERVERNOTIFYUNREGISTER = 0
    SERVERPROCESSSTOP = 0
    SERVERQUERYCMD = 5
    SERVERREQUESTCONNECTIONINFO  = 0
    SERVERSNAPSHOTCREATE = 0
    SERVERSNAPSHOTDEPLOY = 0
    SERVERSTART = 0
    SERVERSTOP = 0
    SERVERTEMPPASSWORDADD = 5
    SERVERTEMPPASSWORDDEL = 5
    SERVERTEMPPASSWORDLIST = 5
    SERVERVARIABLE = 0
    SETCLIENTCHANNELGROUP = 25
    SETCONNECTIONINFO = 0
    SETWHISPERLIST = 0
    TEXTMESSAGESEND = 15
    TOKENADD = 5
    TOKENDELETE = 5
    TOKENLIST = 5
    TOKENUSE = 5
    USE = 0
    VERIFYCHANNELPASSWORD = 5
    VERIFYSERVERPASSWORD = 5
    VERSION = 0
    WHOAMI = 0
