from ts3plugin import ts3plugin

from PythonQt.QtGui import QApplication, QCursor, QDialog, QSplitter, QTreeView, QTableView, QHBoxLayout, QVBoxLayout, QCheckBox, QWidget, QItemSelectionModel, QMenu
from PythonQt.QtCore import Qt, QAbstractItemModel, QModelIndex

import ts3, ts3defines


class PropertyModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(QAbstractItemModel, self).__init__(parent)

        self.widget = None

    def setWidget(self, widg):
        self.layoutAboutToBeChanged()
        self.widget = widg
        self.layoutChanged()

    def index(self, row, column, parent):
        if parent.isValid():
            return QAbstractItemModel.index(self, row, column, parent)

        return self.createIndex(row, column)

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, parent):
        if parent.isValid() or self.widget is None:
            return 0
        else:
            return self.widget.metaObject().propertyCount()

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return 2

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        if index.column() == 0:
            return self.widget.metaObject().property(index.row()).name()
        else:
            return self.widget.metaObject().property(index.row()).read(self.widget)

    def headerData(self, section, orientation, role):
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return None

        if section == 0:
            return "Property"
        else:
            return "Value"


class TreeNode(object):
    def __init__(self, row, parent, obj, aid):
        self.row = row
        self.parent = parent
        self.obj = obj
        self.id = aid

class WidgetModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(QAbstractItemModel, self).__init__(parent)

        self.nodes = {}
        self.nextid = 1

        self._getNodes(None)

    def cleanup(self):
        for n in self.nodes:
            self.nodes[n].obj.setProperty("pyTSon_widgetinfo", None)

        self.nodes = {}

    def _getNodes(self, pnode=None):
        if pnode is None:
            for i, w in enumerate(QApplication.topLevelWidgets()):
                node = TreeNode(i, None, w, self.nextid)
                self.nodes[self.nextid] = node

                w.setProperty("pyTSon_widgetinfo", self.nextid)
                self.nextid += 1

                self._getNodes(node)
        else:
            for i, w in enumerate(pnode.obj.children()):
                node = TreeNode(i, pnode, w, self.nextid)
                self.nodes[self.nextid] = node

                w.setProperty("pyTSon_widgetinfo", self.nextid)
                self.nextid += 1

                self._getNodes(node)

    def _getNode(self, row, parent):
        if not parent.isValid():
            obj = QApplication.topLevelWidgets()[row]
            objid = obj.property("pyTSon_widgetinfo")

            if objid is None:
                obj.setProperty("pyTSon_widgetinfo", self.nextid)
                objid = self.nextid
                self.nextid += 1

                self.nodes[objid] = TreeNode(row, None, obj, objid)
            return self.nodes[objid]
        else:
            pnode = self.nodes[parent.internalId()]
            obj = pnode.obj.children()[row]
            objid = obj.property("pyTSon_widgetinfo")

            if objid is None:
                obj.setProperty("pyTSon_widgetinfo", self.nextid)
                objid = self.nextid
                self.nextid += 1

                self.nodes[objid] = TreeNode(row, pnode, obj, objid)
            return self.nodes[objid]

    def index(self, row, column, parent):
        node = self._getNode(row, parent)
        return self.createIndex(row, column, node.id)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        if index.internalId() not in self.nodes:
            return QModelIndex()

        node = self.nodes[index.internalId()]
        if node.parent is None:
            return QModelIndex()
        else:
            return self.createIndex(node.parent.row, 0, node.parent.id)

    def rowCount(self, parent):
        if not parent.isValid():
            return len(QApplication.topLevelWidgets())
        else:
            return len(self.nodes[parent.internalId()].obj.children())

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        node = self.nodes[index.internalId()]
        if node.obj.objectName == "":
            return "Class: %s" % node.obj.className()
        else:
            return node.obj.objectName


class InfoDialog(QDialog):
    def __init__(self):
        super(QDialog, self).__init__(None)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.splitter = QSplitter(Qt.Horizontal, self)
        self.leftwidg = QWidget(self)
        self.vlayout = QVBoxLayout(self.leftwidg)
        self.checkbox = QCheckBox("Mark selection", self)
        self.tree = QTreeView(self)
        self.tree.header().hide()
        self.vlayout.addWidget(self.checkbox)
        self.vlayout.addWidget(self.tree)
        self.table = QTableView(self)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.splitter.addWidget(self.leftwidg)
        self.splitter.addWidget(self.table)

        self.hlayout = QHBoxLayout(self)
        self.hlayout.addWidget(self.splitter)

        self.treemodel = WidgetModel(self.tree)
        self.tree.setModel(self.treemodel)

        self.tablemodel = PropertyModel(self.table)
        self.table.setModel(self.tablemodel)

        self.stylesheet = None

        self.connect("finished(int)", self.onClosed)
        self.tree.selectionModel().connect("currentChanged(const QModelIndex&, const QModelIndex&)", self.onTreeSelectionChanged)
        self.tree.connect("doubleClicked(const QModelIndex&)", self.onTreeDoubleClicked)
        self.checkbox.connect("toggled(bool)", self.onCheckBoxClicked)

        self.resize(800, 500)

    def onClosed(self):
        if self.checkbox.isChecked() and self.stylesheet is not None:
            index = self.tree.selectionModel().currentIndex
            if index.isValid():
                obj = self.treemodel.nodes[index.internalId()].obj
                if hasattr(obj, "setStyleSheet"):
                    obj.setStyleSheet(self.stylesheet)

        self.treemodel.cleanup()

    def setWidget(self, widg):
        self.widget = widg

        node = self.treemodel.nodes[widg.property("pyTSon_widgetinfo")]
        index = self.treemodel.createIndex(node.row, 0, node.id)
        self.tree.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)
        self.tree.scrollTo(index)

        while index.isValid():
            self.tree.expand(index)
            index = index.parent()

        self.tablemodel.setWidget(widg)

    def onTreeDoubleClicked(self, index):
        obj = self.treemodel.nodes[index.internalId()].obj

        if obj.inherits("QMenu"):
            obj.popup(QCursor.pos())


    def onTreeSelectionChanged(self, cur, prev):
        obj = self.treemodel.nodes[cur.internalId()].obj

        self.tablemodel.setWidget(obj)

        if self.checkbox.isChecked():
            if prev.isValid() and self.stylesheet is not None:
                oldobj = self.treemodel.nodes[prev.internalId()].obj
                if hasattr(oldobj, "setStyleSheet"):
                    oldobj.setStyleSheet(self.stylesheet)

            if hasattr(obj, "setStyleSheet"):
                self.stylesheet = obj.styleSheet
                obj.setStyleSheet("background: red;")

    def onCheckBoxClicked(self, act):
        index = self.tree.selectionModel().currentIndex
        if not index.isValid():
            return

        obj = self.treemodel.nodes[index.internalId()].obj
        if not hasattr(obj, "setStyleSheet"):
            return

        if act:
            self.stylesheet = obj.styleSheet
            obj.setStyleSheet("background: red;")
        elif self.stylesheet is not None:
            obj.setStyleSheet(self.stylesheet)


class widgetinfo(ts3plugin):
    name = "widgetinfo"
    requestAutoload = True
    version = "1.0"
    apiVersion = 21
    author = "Thomas \"PLuS\" Pathmann"
    description = "Show information of the client's ui elements"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Widget info", "icon.png")]
    hotkeys = [("info", "Show widget info")]

    def __init__(self):
        self.dlg = None

    def stop(self):
        pass

    def showInfo(self, widg=None):
        if not self.dlg:
            self.dlg = InfoDialog()

        if widg is not None:
            self.dlg.setWidget(widg)

        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

    def onHotkeyEvent(self, keyword):
        if keyword == "info":
            self.showInfo(QApplication.instance().widgetAt(QCursor.pos()))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.showInfo(None)
