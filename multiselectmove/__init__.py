from ts3plugin import ts3plugin

import ts3lib, ts3defines, ts3widgets

from PythonQt.QtGui import QApplication, QDialog, QAbstractItemView, QTreeView, QHBoxLayout, QItemSelection, QItemSelectionModel
from PythonQt.QtCore import Qt, QEvent, QTimer, QMimeData, QModelIndex
from PythonQt.pytson import EventFilterObject


class DragDropServerviewModel(ts3widgets.ServerviewModel):
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
            if type(c) is ts3widgets.Client:
                if c.clid not in l:
                    l.append(c.clid)
            else:
                self._recursiveClients(c, l)

    def mimeData(self, indexes):
        try:
            clids = []

            for idx in indexes:
                obj = self._indexObject(idx)
                if type(obj) is ts3widgets.Client:
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
        if type(obj) is not ts3widgets.Channel:
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
        assert type(chan) is ts3widgets.Channel

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


class DragDropServerview(QTreeView):
    def __init__(self, schid, parent=None):
        super().__init__(parent)

        try:
            self.svmodel = DragDropServerviewModel(schid, None, self)

            delegate = ts3widgets.ServerviewDelegate(self)
        except Exception as e:
            self.delete()
            raise e

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

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


class MultiSelectDialog(QDialog):
    def __init__(self, schid, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setWindowTitle("Multiselect move")

        self.lay = QHBoxLayout(self)
        self.tree = DragDropServerview(schid, self)
        self.lay.addWidget(self.tree)

        self.resize(400, 600)

    def select(self, firstid, firsttype, secid, sectype, action):
        self.tree.select(firstid, firsttype, secid, sectype, action)


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


class multiselectmove(ts3plugin):
    name = "multiselectmove"
    requestAutoload = False
    version = "1.0.0"
    apiVersion = 21
    author = "Thomas \"PLuS\" Pathmann"
    description = "This plugin makes it possible to move multiple clients around per Multiselect. Just select two items with shift- or control-modifier pressed."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = ""
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "MultiSelectMove", "")]
    hotkeys = [("0", "Show Multiselect window")]

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
                tree.installEventFilter(self.treekeyobserver)
        else:
            QTimer.singleShot(300, self.retrieveWidgets)

    def showDialog(self, schid, firstid=None, firsttype=None, secid=None, sectype=None, action=None):
        if schid not in self.dlgs or not self.dlgs[schid]:
            self.dlgs[schid] = MultiSelectDialog(schid)

        if firstid:
            self.dlgs[schid].select(firstid, firsttype, secid, sectype, action)

        self.dlgs[schid].show()
        self.dlgs[schid].raise_()
        self.dlgs[schid].activateWindow()

    def infoData(self, schid, aid, atype):
        curschid = ts3lib.getCurrentServerConnectionHandlerID()
        if schid != curschid:
            return []

        if schid in self.last and (aid, atype) != self.last[schid]:
            if self.shift:
                self.showDialog(schid, self.last[schid][0], self.last[schid][1], aid, atype, "shift")
            elif self.control:
                self.showDialog(schid, self.last[schid][0], self.last[schid][1], aid, atype, "control")

        self.last[schid] = (aid, atype)
        return []

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.showDialog(schid)

    def onHotkeyEvent(self, keyword):
        if keyword == "0":
            self.showDialog(ts3lib.getCurrentServerConnectionHandlerID())

