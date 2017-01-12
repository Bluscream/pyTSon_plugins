from ts3plugin import ts3plugin
from PythonQt.QtGui import QApplication, QTextDocument
from PythonQt.QtCore import Qt
import ts3, ts3defines

class infoHTML(ts3plugin):
    name = "Extended HTML Support"
    requestAutoload = False
    version = "1.0"
    apiVersion = 21
    author = "Bluscream"
    description =  "Extends the infoData Frame for extended HTML support."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    enabled = False
    InfoFrame = None

    def __init__(self):
        try:
            self.InfoFrame = self.getWidgetByObjectName("InfoFrame").findChild(QTextDocument)
        except: pass
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        if not newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        if not self.enabled:
            self.InfoFrame = self.getWidgetByObjectName("InfoFrame").findChild(QTextDocument)
            ts3.printMessageToCurrentTab("[u]"+str(self.InfoFrame)+"[/u]")
            self.InfoFrame.connect("contentsChanged()", self.onInfoUpdated)
            self.enabled = True
    def onInfoUpdated(self):
        ts3.printMessageToCurrentTab("self:"+str(self))
        ts3.printMessageToCurrentTab(self.__annotations__())
        if hasattr(self, "toHtml"):
            html = str(self.InfoFrame.toHtml())
            if not '<div id="infoHTML" />' in html:
                ts3.printMessageToCurrentTab(html)
                self.InfoFrame.setHtml(html+'<img src="https://i.imgur.com/05aBySW.gif" />test<div id="infoHTML" />')
                ts3.printMessageToCurrentTab("Info Frame updated")
    def getWidgetByObjectName(self, name):
        QApp = QApplication.instance()
        widgets = QApp.topLevelWidgets()
        widgets = widgets + QApp.allWidgets()
        for x in widgets:
            if str(x.objectName) == name: return x
    def getWidgetByClassName(self, name):
        QApp = QApplication.instance()
        widgets = QApp.topLevelWidgets()
        widgets = widgets + QApp.allWidgets()
        for x in widgets:
            if str(x.__class__) == name: return x
