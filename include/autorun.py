import os, requests, json, configparser, webbrowser, traceback, urllib.parse, ts3defines
from datetime import datetime
from ts3 import *
from ts3plugin import *
from ts3help import *
from ts3query import *
from pytsonui import *
from PythonQt.QtGui import *
from PythonQt.QtCore import *

def log(message, channel=ts3defines.LogLevel.LogLevel_INFO, server=0):
        message = str(message)
        _f = '[{:%H:%M:%S}]'.format(datetime.now())+" ("+str(channel)+") "
        if server > 0:
            _f += "#"+str(server)+" "
        _f += "Console> "+message
        ts3.logMessage(message, channel, "pyTSon Console", server)
        ts3.printMessageToCurrentTab(_f)
        # if PluginHost.shell:
        #     PluginHost.shell.appendLine(_f)
        print(_f)

def toggle(boolean):
    boolean = not boolean
    return boolean

def alert(message, title="pyTSon"):
    _a = QMessageBox()
    _a.show()

def m():
    self = PythonConsole()
    _a = QInputDialog.getMultiLineText(self, "pyTSon", "Eval:")
    if _a != "":
        try:
            try:
                res = eval(cmd, self.globals)
                if res != None:
                    self.appendLine(repr(res))
            except SyntaxError:
                exec(cmd, self.globals)
        except:
            self.appendLine(traceback.format_exc())

urlrequest = False
def url(url):
    from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
    if urlrequest: return
    urlrequest = QNetworkAccessManager()
    urlrequest.connect("finished(QNetworkReply*)", urlResponse)
    urlrequest.get(QNetworkRequest(QUrl(url)))
def urlResponse(reply):
    from PythonQt.QtNetwork import QNetworkReply
    if reply.error() == QNetworkReply.NoError:
        return reply.readAll().data().decode('utf-8')
    else:
        err = ts3.logMessage("Error checking for update: %s" % reply.error(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon.PluginHost.updateCheckFinished", 0)
        if err != ts3defines.ERROR_ok:
            print("Error checking for update: %s" % reply.error())
    urlrequest.delete()
    urlrequest = None

i = QApplication.instance()
schid = ts3.getCurrentServerConnectionHandlerID()
error, ownid = ts3.getClientID(schid)
if error == ts3defines.ERROR_ok:
    error, ownnick = ts3.getClientDisplayName(schid, ownid)
    if error == ts3defines.ERROR_ok:
        def pcmd(cmd):
            ts3.sendPluginCommand(schid, cmd, ts3defines.PluginTargetMode.PluginCommandTarget_MAX, [])
            ts3.sendPluginCommand(schid, cmd, ts3defines.PluginTargetMode.PluginCommandTarget_CURRENT_CHANNEL_SUBSCRIBED_CLIENTS, [])
            ts3.sendPluginCommand(schid, cmd, ts3defines.PluginTargetMode.PluginCommandTarget_CLIENT, [ownid])
            ts3.sendPluginCommand(schid, cmd, ts3defines.PluginTargetMode.PluginCommandTarget_SERVER, [])
            ts3.sendPluginCommand(schid, cmd, ts3defines.PluginTargetMode.PluginCommandTarget_CURRENT_CHANNEL, [])
            log(cmd, ts3defines.LogLevel.LogLevel_INFO, schid)
        def p(c, cmd="test command%$%test command%$%"):
            if c == 0:
                print("Sent command "+cmd+" to PluginCommandTarget_CURRENT_CHANNEL")
            elif c == 1:
                print("Sent command "+cmd+" to PluginCommandTarget_SERVER")
            elif c == 2:
                print("Sent command "+cmd+" to PluginCommandTarget_CLIENT")
                ts3.sendPluginCommand(schid, cmd, c, [ownid])
                return
            elif c == 3:
                print("Sent command "+cmd+" to PluginCommandTarget_CURRENT_CHANNEL_SUBSCRIBED_CLIENTS")
            elif c == 4:
                print("Sent command "+cmd+" to PluginCommandTarget_MAX")
            ts3.sendPluginCommand(schid, cmd, c, [])
# def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
#     print(errorMessage)
#
# def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
#     print(errorMessage)

print('(pyTSon Console started at: {:%Y-%m-%d %H:%M:%S})'.format(datetime.now()))
for item in sys.path:
    print('"'+item+'"')
print("")
print(sys.flags)
print("")
print(sys.executable+" "+sys.platform+" "+sys.version+" API: "+str(sys.api_version))
print("")

# void enumerateMenu(QMenu *menu)
# {
#     foreach (QAction *action, menu->actions()) {
#         if (action->isSeparator()) {
#             qDebug("this action is a separator");
#         } else if (action->menu()) {
#             qDebug("action: %s", qUtf8Printable(action->text()));
#             qDebug(">>> this action is associated with a submenu, iterating it recursively...");
#             enumerateMenu(action->menu());
#             qDebug("<<< finished iterating the submenu");
#         } else {
#             qDebug("action: %s", qUtf8Printable(action->text()));
#         }
#     }
# }
