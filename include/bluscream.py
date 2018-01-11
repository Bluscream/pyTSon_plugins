from datetime import datetime
from PythonQt.QtGui import QInputDialog, QMessageBox, QDialog
from PythonQt.QtCore import Qt
from ts3plugin import PluginHost
import ts3lib, ts3defines

# GENERAL FUNCTIONS #


def timestamp():
    return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

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
    ts3lib.logMessage("{}: schid = {} | err = {} | afreduce = {} | cmdblock = {} | ipblock = {} | points_per_action = {} |interval = {}".format(name, schid, err, afreduce, cmdblock, ipblock, command, interval), ts3defines.LogLevel.LogLevel_INFO, "pyTSon", 0)
    return interval

# TS3Hook #

def sendCommand(name, cmd, schid=0):
    if PluginHost.cfg.getboolean("general", "verbose"):
        ts3lib.printMessage(ts3lib.getCurrentServerConnectionHandlerID(), '{timestamp} [color=orange]{name}[/color]:[color=white] {message}'.format(timestamp=timestamp(), name=name, message=cmd), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
    cmd = cmd.replace(" ", "~s")
    if schid == 0: schid = ts3lib.getCurrentServerConnectionHandlerID()
    ts3lib.requestSendServerTextMsg(schid, "~cmd{}".format(cmd))
