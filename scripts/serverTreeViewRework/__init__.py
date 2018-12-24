import os

from ts3plugin import ts3plugin

import ts3lib, ts3defines
from ts3widgets.serverview import ServerviewModel, ServerviewDelegate, Client, Channel, Server

from PythonQt import BoolResult
from PythonQt.QtGui import (QApplication, QDialog, QAbstractItemView,
                            QTreeView, QHBoxLayout, QItemSelection,
                            QItemSelectionModel, QTextDocument, QWidget, QInputDialog, QLineEdit)
from PythonQt.QtCore import Qt, QEvent, QTimer, QMimeData, QModelIndex
from PythonQt.pytson import EventFilterObject


class DragDropServerviewModel(ServerviewModel):
    def __init__(self, schid, iconpack=None, parent=None):
        super().__init__(schid, iconpack, parent)

        self.mimecache = []

    def flags(self, index):
        default = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        if index.isValid():
            return default | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        else:
            return default

    def mimeTypes(self):
        return ["text/plain"]

    def supportedDropActions(self):
        return Qt.MoveAction

    def _recursiveClients(self, chan, l):
        for c in chan:
            if type(c) is Client:
                if c.clid not in l:
                    l.append(c.clid)
            else:
                self._recursiveClients(c, l)

    def mimeData(self, indexes):
        try:
            clids = []

            for idx in indexes:
                obj = self._indexObject(idx)
                if type(obj) is Client:
                    if obj.clid not in clids:
                        clids.append(obj.clid)
                else:
                    self._recursiveClients(obj, clids)

            mimedata = QMimeData()
            mimedata.setText(" ".join(map(str, clids)))
            self.mimecache.append(mimedata) #we have to keep this in scope!

            return mimedata
        except Exception as e:
            print("exception in mimeData: %s" % e)
            return 0

    def canDropMimeData(self, mimedata, action, row, column, parent):
        if not mimedata.hasText() or not parent.isValid() or not action & self.supportedDropActions() or row != -1:
            return False

        obj = self._indexObject(parent)
        if type(obj) is not Channel:
            return False

        return True

    def dropMimeData(self, mimedata, action, row, column, parent):
        if action != Qt.MoveAction:
            return False

        if not mimedata.hasText():
            return False

        if mimedata.text() == "":
            return True

        chan = self._indexObject(parent)
        assert type(chan) is Channel

        for clid in map(int, mimedata.text().split(" ")):
            err = ts3lib.requestClientMove(self.schid, clid, chan.cid, "")
            if err != ts3defines.ERROR_ok:
                print("error moving: %s" % err)

        return True

    def getClientIndex(self, clid):
        obj = self.allclients[clid]
        return self._createIndex(obj.rowOf(), 0, obj)

    def getChannelIndex(self, cid):
        obj = self.allchans[cid]
        return self._createIndex(obj.rowOf(), 0, obj)

    def getServerIndex(self):
        return self._createIndex(0, 0, self.root)

    def highestIndex(self, indexes, node=None):
        if len(indexes) == 0:
            return -1

        if not node:
            node = self.index(0, 0, QModelIndex())

        for i in range(len(indexes)):
            if node == indexes[i]:
                return i

        for k in range(self.rowCount(node)):
            for i in range(len(indexes)):
                kidx = self.index(k, 0, node)
                if indexes[i] == kidx:
                    return i

                recursive = self.highestIndex(indexes, kidx)
                if recursive != -1:
                    return recursive

        return -1

    def dfs(self, startidx, lastidx, l):
        ret = []

        paridx = startidx.parent()
        #startidx and the siblings below
        for i in range(startidx.row(), self.rowCount(paridx)):
            idx = self.index(i, 0, paridx)
            l.append(idx)

            if idx == lastidx:
                return True

            #childs of current sibling
            if self.rowCount(idx) > 0:
                if self.dfs(self.index(0, 0, idx), lastidx, l):
                    return True

        #siblings below paridx
        parparidx = paridx.parent()
        if parparidx.isValid() and self.rowCount(parparidx) > paridx.row() +1:
            if self.dfs(self.index(paridx.row() +1, 0, parparidx), lastidx, l):
                return True

        return False

def inputBox(parent, title, text, default=""):
    """
    :param default:
    :param title:
    :param text:
    :return:
    """
    x = QWidget(parent)
    x.setAttribute(Qt.WA_DeleteOnClose)
    ok = BoolResult()
    text = QInputDialog.getText(x, title, text, QLineEdit.Normal, default, ok)
    if ok: return text
    else: return False

class DragDropServerview(QTreeView):
    def __init__(self, schid, parent=None):
        super().__init__(parent)

        try:
            self.svmodel = DragDropServerviewModel(schid, None, self)

            delegate = ServerviewDelegate(self)
        except Exception as e:
            self.delete()
            raise e

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setExpandsOnDoubleClick(False)
        self.schid = schid
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setObjectName("CustomServerTreeView{}".format(schid))
        #self.setAnimated(True) #FIXME: everything under that gets black or smth

        if parent:
            self.resize(parent.size)

        self.header().hide()

        self.setItemDelegate(delegate)

        self.setModel(self.svmodel)

        self.expandAll()

    def select(self, firstid, firsttype, secid, sectype, action):
        self.clearSelection()

        if firsttype == ts3defines.PluginItemType.PLUGIN_CLIENT:
            firstidx = self.svmodel.getClientIndex(firstid)
        elif firsttype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
            firstidx = self.svmodel.getChannelIndex(firstid)
        else:
            firstidx = self.svmodel.getServerIndex()

        if sectype == ts3defines.PluginItemType.PLUGIN_CLIENT:
            secidx = self.svmodel.getClientIndex(secid)
        elif sectype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
            secidx = self.svmodel.getChannelIndex(secid)
        else:
            secidx = self.svmodel.getServerIndex()

        if action == "control":
            self.selectionModel().select(firstidx, QItemSelectionModel.SelectCurrent)
            self.selectionModel().select(secidx, QItemSelectionModel.Select)
        elif action == "shift":
            if self.svmodel.highestIndex([firstidx, secidx]) != 0:
                firstidx, secidx = secidx, firstidx

            between = []
            if self.svmodel.dfs(firstidx, secidx, between):
                for idx in between:
                    self.selectionModel().select(idx, QItemSelectionModel.Select)

    def indexToObject(self, index):
        """
        Returns the underlying object of a QModelIndex.
        @param index: the index of the model
        @type index: QModelIndex
        @return: the wrapped viewitem
        @rtype: Server or Channel or Client
        """
        if self.svmodel:
            return self.svmodel._indexObject(index)
        else:
            return None

    def onItemClicked(self, index):
        try:
            item = self.indexToObject(index)
            if not item:
                return
            treeView = self.parent()
            if type(item) is Client:
                treeView.clientSelect(item.clid)
            elif type(item) is Channel:
                treeView.channelSelect(item.cid)
            elif type(item) is Server:
                treeView.setCurrentIndex(treeView.model().index(0,0)) #Select the first item as it is always the server
                treeView.serverSelect() #then force refresh the infoframe
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def mouseDoubleClickEvent(self, event):
        try:
            if event.button() != Qt.LeftButton:
                return

            index = self.indexAt(event.pos())
        
            item = self.indexToObject(index)
            if not item:
                return
            if type(item) is Client:
                #open chat
                if item.isme: #don't chat with your self. get friends. TODO: change your name
                    #TODO: self.edit(index)
                    return
                treeView = self.parent()
                serverView = treeView.parent()
                #TODO: find better way to select or better way to open chat #TODO: maybe indexAt (needs same layout as old view tho) #set the original tree view index to our current
                #found = BoolResult()
                treeView.onSearchItemByName(item.name, QTextDocument.FindCaseSensitively | QTextDocument.FindWholeWords, True, False, True)
                #if found:
                serverView.onOpenChatRequest() #onOpenChatRequest(anyID) is useless (prolly called from action menu; opens chat tab for selected client)
            elif type(item) is Channel:
                #join channel
                (err, clid) = ts3lib.getClientID(self.schid)
                if err != ts3defines.ERROR_ok:
                    return
                if item.hasClient(clid): #check if we're already in the channel
                    return
                if not item.isPasswordProtected:
                    ts3lib.requestClientMove(self.schid, clid, item.cid, "")
                else:
                    pw = item.getPassword(True)
                    ts3lib.requestClientMove(self.schid, clid, item.cid, pw)
            #elif type(item) is Server:
                #do nothing i guess?
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def onContextMenu(self, pos):
        try:
            originalTreeView = self.parent()
            originalTreeView.setCurrentIndex(originalTreeView.indexAt(pos)) #FIXME: this requires the trees to be in perfect sync
            originalTreeView.customContextMenuRequested(pos)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def onSearch(name, flags, isRepeat, searchAllTabs, found): #TODO: this
        try:
            if not searchAllTabs:
                if self.schid != ts3lib.getCurrentServerConnectionHandlerID():
                    return
            
            #ret = self.svmodel.find(name, flags)       
            #ts3lib.printMessageToCurrentTab(str(ret))
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

class NewServerTreeView():
    def __init__(self, schid, parent=None):
        self.lay = QHBoxLayout(parent)
        self.tree = DragDropServerview(schid, parent)
        self.lay.addWidget(self.tree)
        self.lay.setContentsMargins(0,0,0,0)
        parent.setLayout(self.lay)

        self.tree.connect("clicked(QModelIndex)", self.tree.onItemClicked)
        self.tree.connect("customContextMenuRequested(QPoint)", self.tree.onContextMenu)

        self.searchFrame = [item for item in QApplication.instance().allWidgets() if type(item).__name__ == "SearchFrame"][0]
        self.searchFrame.connect("find(QString,QTextDocument::FindFlags,bool,bool,bool&)", self.tree.onSearch)
    
    def close(self):
        self.lay.removeWidget(self.tree)
        self.lay.deleteLater()
        self.tree.setParent(None) #no parent-> child of python -> gets garbage collected when out of scope #maybe use deleteLater

    def select(self, firstid, firsttype, secid, sectype, action):
        self.tree.select(firstid, firsttype, secid, sectype, action)

    def show(self):
        self.tree.show()

    def raise_(self):
        self.tree.raise_()

    def toggle(self):
        if self.tree.isHidden():
            self.show()
        else:
            self.hide()

    def show(self):
        self.tree.show()
        self.tree.raise_()

    def hide(self):
        self.tree.hide()


def findChildWidget(widget, checkfunc, recursive):
    for c in widget.children():
        if c.isWidgetType():
            if checkfunc(c):
                return c
            elif recursive:
                recret = findChildWidget(c, checkfunc, recursive)
                if recret:
                    return recret

    return None


def findAllChildWidgets(widget, checkfunc, recursive):
    ret = []
    for c in widget.children():
        if c.isWidgetType():
            if checkfunc(c):
                ret.append(c)
            elif recursive:
                ret += findAllChildWidgets(c, checkfunc, recursive)

    return ret


class serverTreeViewRework(ts3plugin):
    name = "ServerTreeViewRework"
    requestAutoload = False
    version = "1.0.1"
    apiVersion = 21
    author = "bluscream, exp111, Thomas \"PLuS\" Pathmann"
    description = "A new ServerTree. Build on MultiSelectMove."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = ""
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "ToggleServerTreeView", os.path.join("ressources", "octicons", "git-pull-request.svg.png"))]
    hotkeys = [("0", "Toggle ServerTreeView")]

    def __init__(self):
        self.svobserver = EventFilterObject([QEvent.ChildAdded])
        self.svobserver.connect("eventFiltered(QObject*, QEvent*)", self.onNewServerview)

        self.treekeyobserver = EventFilterObject([QEvent.KeyPress, QEvent.KeyRelease, QEvent.FocusOut])
        self.treekeyobserver.connect("eventFiltered(QObject*, QEvent*)", self.onTreeKey)

        self.main = None
        self.svmanagerstack = None

        self.control = False
        self.shift = False

        self.last = {}
        self.dlgs = {}
        self.autoStart = True

        self.retrieveWidgets()

    def stop(self):
        self.svobserver.delete()
        self.treekeyobserver.delete()

        for schid, dlg in self.dlgs.items():
            if dlg:
                dlg.close()

    def onNewServerview(self, obj, ev):
        #this will cause to install eventfilters on the trees
        self.retrieveWidgets()

    def onTreeKey(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Control:
                self.control = True
            elif event.key() == Qt.Key_Shift:
                self.shift = True
        elif event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Control:
                self.control = False
            elif event.key() == Qt.Key_Shift:
                self.shift = False
        elif event.type() == QEvent.FocusOut:
            self.control = False
            self.shift = False

    def retrieveWidgets(self):
        if not self.main:
            for w in QApplication.instance().topLevelWidgets():
                if "MainWindow" in str(type(w)):
                    self.main = w
                    break

        if self.main and not self.svmanagerstack:
            self.svmanagerstack = findChildWidget(self.main, lambda x: x.objectName == "qt_tabwidget_stackedwidget" and "ServerViewManager" in str(type(x.parent())), True)

        if self.svmanagerstack:
            self.svmanagerstack.installEventFilter(self.svobserver)
            for tree in findAllChildWidgets(self.svmanagerstack, lambda x: "TreeView" in str(type(x)), True):
                #TODO: maybe create a new servertreeview here?
                tree.installEventFilter(self.treekeyobserver)
        else:
            QTimer.singleShot(300, self.retrieveWidgets)


    def toggleDialog(self, schid):
        if schid not in self.dlgs or not self.dlgs[schid]:
            if not self.svmanagerstack: #We need the tabmanager to see which is the current active treeview/tab
                self.retrieveWidgets()
            #FIXME: get proper serverview for schid
            currentServerTree = [item for item in self.svmanagerstack.widget(self.svmanagerstack.currentIndex).children() if item.objectName == "ServerTreeView"][0]
            self.dlgs[schid] = NewServerTreeView(schid, currentServerTree) #create a new serverview over the old one as a child

        self.dlgs[schid].toggle()

    def showDialog(self, schid):
        if schid not in self.dlgs or not self.dlgs[schid]:
            if not self.svmanagerstack: #We need the tabmanager to see which is the current active treeview/tab
                self.retrieveWidgets()
            #FIXME: get proper serverview for schid
            currentServerTree = [item for item in self.svmanagerstack.widget(self.svmanagerstack.currentIndex).children() if item.objectName == "ServerTreeView"][0]
            self.dlgs[schid] = NewServerTreeView(schid, currentServerTree) #create a new serverview over the old one as a child

        self.dlgs[schid].show()

    def hideDialog(self, schid):
        if schid in self.dlgs and self.dlgs[schid]:
            self.dlgs[schid].hide()

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.toggleDialog(schid)

    def onHotkeyEvent(self, keyword):
        if keyword == "0":
            self.toggleDialog(ts3lib.getCurrentServerConnectionHandlerID())

