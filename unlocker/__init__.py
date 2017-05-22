from ts3plugin import ts3plugin, PluginHost
from ts3lib import logMessage, printMessageToCurrentTab
import ts3defines
from PythonQt.QtGui import *
from PythonQt.QtCore import *

class info(ts3plugin):
    name = "Unlocker"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Shows you more informations.\nBest to use together with a Extended Info Theme.\nClick on \"Settings\" to select what items you want to see :)\n\nHomepage: https://github.com/Bluscream/Extended-Info-Plugin\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Unlock everything", "")]
    hotkeys = [("gui_unlock", "Unlock everything")]

    def __init__(self):
        logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)

    def unlock(self, show=False):
        i = QApplication.instance()
        for item in i.allWidgets():
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


    def lock(self, show=False):
        i = QApplication.instance()
        for item in i.allWidgets():
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
            if show:
                try: item.setHidden(True)
                except: pass

    def onHotkeyEvent(self, keyword):
        if keyword == "gui_unlock":
            self.unlock()

    def onMenuItemEvent(self, a, b, c, d):
        if c == 0:
            self.unlock()
