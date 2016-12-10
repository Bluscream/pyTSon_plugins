import os, requests, json, configparser, webbrowser, traceback, urllib.parse, ts3defines
from datetime import datetime
from ts3 import *
from ts3plugin import *
from ts3help import *
from ts3query import *
from pytsonui import *
from PythonQt.QtGui import *
from PythonQt.QtCore import *
from PythonQt.QtNetwork import *
from PythonQt.Qt import *
from PythonQt.private import *
self = QApplication.instance()
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

schid = ts3.getCurrentServerConnectionHandlerID()
(error, ownid) = ts3.getClientID(schid)
def unlock(show=False):
    for item in self.allWidgets():
        try: item.setEnabled(True)
        except: pass
        try: item.setCheckable(True)
        except: pass
        try: item.setDragEnabled(True)
        except: pass
        try: item.setDragDropMode(QAbstractItemView.DragDrop)
        except: pass
        try: item.setSelectionMode(QAbstractItemView.MultiSelection)
        except: pass
        try: item.setSelectionBehavior(QAbstractItemView.SelectItems)
        except: pass
        try: item.setResizeMode(QListView.Adjust)
        except: pass
        try: item.setSortingEnabled(True)
        except: pass
        try:
            if item.ContextMenuPolicy() == Qt.PreventContextMenu:
                item.setContextMenuPolicy(Qt.NoContextMenu)
        except: pass
        try:
            if "background:red;" in item.styleSheet:
                item.styleSheet = item.styleSheet.replace("background:red;", "")
        except: logMessage("error", ts3defines.LogLevel.LogLevel_INFO, "QSS", 0);pass
        try: item.setTextInteractionFlag(Qt.TextEditable)
        except: pass
        try: item.setUndoRedoEnabled(True)
        except: pass
        try: item.setReadOnly(False)
        except: pass
        try: item.clearMinimumDateTime()
        except: pass
        try: item.clearMaximumDateTime()
        except: pass
        try: item.clearMinimumTime()
        except: pass
        try: item.clearMaximumTime()
        except: pass
        try: item.clearMinimumDate()
        except: pass
        try: item.clearMaximumDate()
        except: pass
        try: item.setDateEditEnabled(True)
        except: pass
        try: item.setTextVisible(True)
        except: pass
        try: item.setHeaderHidden(False)
        except: pass
        try: item.setItemsExpandable(True)
        except: pass
        try: item.setModality(Qt.NonModal)
        except: pass
        if show:
            try: item.setHidden(False)
            except: pass
            try: item.show()
            except: pass
            try: item.raise_()
            except: pass
            try: item.activateWindow()
            except: pass
def lock(show=False):
    for item in self.allWidgets():
        try: item.setEnabled(False)
        except: pass
        try: item.setCheckable(False)
        except: pass
        try: item.setDragEnabled(False)
        except: pass
        try: item.setDragDropMode(QAbstractItemView.NoDragDrop)
        except: pass
        try: item.setSelectionMode(QAbstractItemView.NoSelection)
        except: pass
        try: item.setSelectionBehavior(QAbstractItemView.SelectItems)
        except: pass
        try: item.setResizeMode(QListView.Adjust)
        except: pass
        try: item.setResizeMode(QHeaderView.Interactive)
        except: pass
        try: item.setSectionResizeMode(QHeaderView.Interactive)
        except: pass
        try: item.setSortingEnabled(False)
        except: pass
        try: item.setContextMenuPolicy(Qt.PreventContextMenu)
        except: pass
        try: item.styleSheet = ""
        except: pass
        try: item.setTextInteractionFlag(Qt.NoTextInteraction)
        except: pass
        try: item.setUndoRedoEnabled(False)
        except: pass
        try: item.setReadOnly(True)
        except: pass
        try: item.setDateEditEnabled(True)
        except: pass
        try: item.setTextVisible(True)
        except: pass
        try: item.setHeaderHidden(False)
        except: pass
        try: item.setItemsExpandable(True)
        except: pass
        try: item.setModality(Qt.ApplicationModal)
        except: pass
        try: item.clicked.disconnect()
        except: pass
        if show:
            try: item.setHidden(True)
            except: pass

def findWidget(name):
    try:
        name = name.lower()
        widgets = self.topLevelWidgets()
        widgets = widgets + self.allWidgets()
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
def widgetbyclassname(name):
    widgets = self.topLevelWidgets()
    widgets = widgets + self.allWidgets()
    for x in widgets:
        if name in str(x.__class__).replace("<class '","").replace("'>",""):
            return x
def widgetbyobjectname(name):
    widgets = self.topLevelWidgets()
    widgets = widgets + self.allWidgets()
    for x in widgets:
        if str(x.objectName) == name:
            return x
def getobjects(name, cls=True):
    import gc
    objects = []
    for obj in gc.get_objects():
        if (isinstance(obj, QObject) and
            ((cls and obj.inherits(name)) or
             (not cls and obj.objectName() == name))):
            objects.append(obj)
    return objects

def objects():
    import gc;_ret = []
    for x in gc.get_objects(): _ret.extend(str(repr(x)))
    return _ret

def file(name, content):
    with open(os.path.expanduser("~/Desktop/"+name+".txt"), "w") as text_file:
        print(str(content), file=text_file)

#if error == 0:
    #error, ownnick = ts3.getClientDisplayName(schid, ownid)
    # if error == 0:
    #     def p(c, cmd="test", clid=0):
    #         if c == 0:
    #             print("Sent command "+cmd+" to PluginCommandTarget_CURRENT_CHANNEL")
    #         elif c == 1:
    #             print("Sent command "+cmd+" to PluginCommandTarget_SERVER")
    #         elif c == 2:
    #             print("Sent command "+cmd+" to PluginCommandTarget_CLIENT")
    #             ts3.sendPluginCommand(schid, cmd, c, [clid])
    #             return
    #         elif c == 3:
    #             print("Sent command "+cmd+" to PluginCommandTarget_CURRENT_CHANNEL_SUBSCRIBED_CLIENTS")
    #         elif c == 4:
    #             print("Sent command "+cmd+" to PluginCommandTarget_MAX")
    #         ts3.sendPluginCommand(schid, cmd, c, [])

print('(pyTSon Console started at: {:%Y-%m-%d %H:%M:%S})'.format(datetime.now()))
for item in sys.path:
    print('"'+item+'"')
print("")
print(sys.flags)
print("")
print(sys.executable+" "+sys.platform+" "+sys.version+" API: "+str(sys.api_version))
print("")

class testClass(object):
    def __init__(): pass
    def testFunction(): pass
