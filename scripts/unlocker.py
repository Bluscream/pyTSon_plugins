from ts3plugin import ts3plugin, PluginHost
import ts3defines
from PythonQt.QtGui import *
from PythonQt.QtCore import *

class info(ts3plugin):
    name = "Unlocker"
    apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Shows you more informations.\nBest to use together with a Extended Info Theme.\nClick on \"Settings\" to select what items you want to see :)\n\nHomepage: https://github.com/Bluscream/Extended-Info-Plugin\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Unlock everything", "")]
    hotkeys = [("gui_unlock", "Unlock everything")]

    def __init__(self):
        print(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)

    def unlock(self):
        i = QApplication.instance()
        for item in i.allWidgets():
            # try: item.setHidden(False)
            # except: continue
            try: item.setEnabled(True)
            except: continue
            try: item.setCheckable(True)
            except: continue
            try: item.setDragEnabled(True)
            except: continue
            try: item.setDragDropMode(QAbstractItemView.DragDrop)
            except: continue
            try: item.setSelectionMode(QAbstractItemView.MultiSelection)
            except: continue
            try: item.setSelectionBehavior(QAbstractItemView.SelectItems)
            except: continue
            try: item.setResizeMode(QListView.Adjust)
            except: continue
            try: item.setSortingEnabled(True)
            except: continue
            try:
                if item.ContextMenuPolicy() == Qt.PreventContextMenu:
                    item.setContextMenuPolicy(Qt.NoContextMenu)
            except: continue
            try: item.setTextInteractionFlag(Qt.TextEditable)
            except: continue
            try: item.setUndoRedoEnabled(True)
            except: continue
            try: item.setReadOnly(False)
            except: continue
            try: item.clearMinimumDateTime()
            except: continue
            try: item.clearMaximumDateTime()
            except: continue
            try: item.clearMinimumTime()
            except: continue
            try: item.clearMaximumTime()
            except: continue
            try: item.clearMinimumDate()
            except: continue
            try: item.clearMaximumDate()
            except: continue
            try: item.setDateEditEnabled(True)
            except: continue
            try: item.setTextVisible(True)
            except: continue
            try: item.setHeaderHidden(False)
            except: continue
            try: item.setItemsExpandable(True)
            except: continue
            try: item.setModality(Qt.ApplicationModal)
            except: continue
            # try: item.show()
            # except: continue
            # try: item.raise_()
            # except: continue
            # try: item.activateWindow()
            # except: continue

    def onHotkeyEvent(self, keyword):
        if keyword == "gui_unlock":
            self.unlock()

    def onMenuItemEvent(self, a, b, c, d):
        if c == 0:
            self.unlock()
