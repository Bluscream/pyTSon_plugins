from ts3plugin import ts3plugin

from PythonQt.QtGui import QApplication, QCursor, QDialog, QSplitter, QTreeView, QTableView, QHBoxLayout, QVBoxLayout, QCheckBox, QWidget, QItemSelectionModel, QMenu
from PythonQt.QtCore import Qt, QAbstractItemModel, QModelIndex

import ts3defines
import traceback

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

class WidgetModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(QAbstractItemModel, self).__init__(parent)

    def index(self, row, column, parent):
        if not parent.isValid():
            if len(QApplication.topLevelWidgets()) <= row:
                return QModelIndex()
            else:
                return self.createIndex(row, column, QApplication.topLevelWidgets()[row])
        else:
            if len(parent.internalPointer().children()) <= row:
                return QModelIndex()
            else:
                return self.createIndex(row, column, parent.internalPointer().children()[row])

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        obj = index.internalPointer()
        tlw = QApplication.topLevelWidgets()

        if obj in tlw:
            return QModelIndex()
        else:
            if obj.parent() in tlw:
                return self.createIndex(tlw.index(obj.parent()), 0, obj.parent())
            else:
                return self.createIndex(obj.parent().children().index(obj), 0, obj.parent())

    def rowCount(self, parent):
        if not parent.isValid():
            return len(QApplication.topLevelWidgets())
        else:
            return len(parent.internalPointer().children())

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        obj = index.internalPointer()
        if obj.objectName == "":
            return "Class: %s" % obj.className()
        else:
            return "%s (Class: %s)" % (obj.objectName, obj.className())


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
                obj = index.internalPointer()
                if hasattr(obj, "setStyleSheet"):
                    obj.setStyleSheet(self.stylesheet)


    def setWidget(self, widg):
        self.widget = widg

        tlw = QApplication.topLevelWidgets()

        if widg in tlw:
            index = self.treemodel.createIndex(tlw.index(widg), 0, widg)
        else:
            index = self.treemodel.createIndex(widg.parent().children().index(widg), 0, widg)

        self.tree.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)
        self.tree.scrollTo(index)

        while index.isValid():
            self.tree.expand(index)
            index = index.parent()

        self.tablemodel.setWidget(widg)

    def onTreeDoubleClicked(self, index):
        obj = index.internalPointer()

        if obj.inherits("QMenu"):
            obj.popup(QCursor.pos())


    def onTreeSelectionChanged(self, cur, prev):
        obj = cur.internalPointer()

        self.tablemodel.setWidget(obj)

        if self.checkbox.isChecked():
            if prev.isValid() and self.stylesheet is not None:
                oldobj = prev.internalPointer()
                if hasattr(oldobj, "setStyleSheet"):
                    oldobj.setStyleSheet(self.stylesheet)

            if hasattr(obj, "setStyleSheet"):
                self.stylesheet = obj.styleSheet
                obj.setStyleSheet("background: red;")

    def onCheckBoxClicked(self, act):
        index = self.tree.selectionModel().currentIndex
        if not index.isValid():
            return

        obj = index.internalPointer()
        if not hasattr(obj, "setStyleSheet"):
            return

        if act:
            self.stylesheet = obj.styleSheet
            obj.setStyleSheet("background: red;")
        elif self.stylesheet is not None:
            obj.setStyleSheet(self.stylesheet)


class widgetinfo(ts3plugin):
    name = "widgetinfo"
    requestAutoload = False
    version = "1.0.1"
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

