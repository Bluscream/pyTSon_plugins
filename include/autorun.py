import os, requests, json, configparser, webbrowser, traceback, urllib.parse, ts3defines
from datetime import datetime
from ts3 import *
from ts3plugin import *
from ts3help import *
from pytsonui import *
from PythonQt.QtGui import *
from PythonQt.QtCore import *

def log(message, channel=ts3defines.LogLevel.LogLevel_INFO, server=0):
        _f = '[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" ("+str(channel)+") Console> "+message
        ts3.logMessage(message, channel, "pyTSon Console", server)
        ts3.printMessageToCurrentTab(_f)
        if PluginHost.shell:
            PluginHost.shell.appendLine(_f)
        print(_f)

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

for item in sys.path:
    print(item)
print("")
print(sys.flags)
print("")
print(sys.executable+" "+sys.platform+" "+sys.version+"API: "+str(sys.api_version))
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
