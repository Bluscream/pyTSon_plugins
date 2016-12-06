from ts3plugin import ts3plugin
from pytsonui import setupUi
from PythonQt.QtGui import QApplication, QCursor, QDialog, QSplitter, QTreeView, QTableView, QHBoxLayout, QVBoxLayout, QCheckBox, QWidget, QItemSelectionModel, QMenu, QMessageBox, QFileDialog
from PythonQt.QtCore import Qt, QAbstractItemModel, QModelIndex
import ts3, ts3defines, os

try:

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
                if hasattr(obj, "setEnabled"):
                    obj.setEnabled(True)
                if hasattr(obj, "setEditable"):
                    obj.setEditable(True)
                #if hasattr(obj, "visible"):
                    #obj.visible = True

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

    class TestDialog(QDialog):
        def __init__(self,this, parent=None):
            super(QDialog, self).__init__(parent)
            setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "devTools", "test.ui"))

    class qssDialog(QDialog):
        def __init__(self, arg, parent=None):
            super(QDialog, self).__init__(parent)
            setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "devTools", "editor.ui"))
            self.resize(1000, 900)
            self.setWindowTitle('Teamspeak Stylesheet Editor : : Developer Tools')
            self.stylesheet = QApplication.instance().styleSheet
            self.qssEditor.setPlainText(self.stylesheet)
            self.lastSave = None
        def on_chk_live_stateChanged(self, state):
            if state == Qt.Checked:
                self.qssEditor.connect('textChanged()', self.onQSSChanged)
                self.btn_apply.setEnabled(False)
            else:
                self.qssEditor.disconnect(self.onQSSChanged)
                self.btn_apply.setEnabled(True)
        def onQSSChanged(self):
            QApplication.instance().styleSheet = self.qssEditor.toPlainText()
        def on_btn_apply_clicked(self):
            QApplication.instance().styleSheet = self.qssEditor.toPlainText()
        def on_btn_insert_clicked(self):
            self.qssEditor.appendPlainText("\n{\n\t:\n}")
        def on_btn_reset_clicked(self):
            if QMessageBox(QMessageBox.Warning, "Reset QSS?", "This will reset your changes to the initial Stylesheet! Continue?", QMessageBox.Ok | QMessageBox.Cancel).exec_() == QMessageBox.Ok:
                QApplication.instance().styleSheet = self.stylesheet
                self.qssEditor.setPlainText(self.stylesheet)
        def on_btn_minify_clicked(self):
            try:
                from css_html_js_minify import css_minify
            except:
                import traceback;QMessageBox.Critical("Can't minify", traceback.format_exc()).exec_();return # _p = "";for item in sys.path: _p += str(item)+"\n" #"Python package \"css_html_js_minify\" could not be loaded from one of the following locations:\n\n"+_p
            _old = self.qssEditor.toPlainText()
            _minified = css_minify(_old, comments=False)
            QApplication.instance().styleSheet = _minified
            self.qssEditor.setPlainText(_minified)
            if QMessageBox(QMessageBox.Warning, "Use minified QSS?", "Your minified QSS code has been applied.\nIf you encounter any issues with the minified code you should click on cancel.", QMessageBox.Ok | QMessageBox.Cancel).exec_() == QMessageBox.Cancel:
                QApplication.instance().styleSheet = _old
                self.qssEditor.setPlainText(_old)
        def on_btn_save_clicked(self):
            _file = None
            if self.lastSave:
                _file = QFileDialog.getSaveFileName(self, "Save Qt Stylesheet", self.lastSave, "Teamspeak 3 Stylesheet File (*.qss)")
            else:
                _file = QFileDialog.getSaveFileName(self, "Save Qt Stylesheet", "", "Teamspeak 3 Stylesheet File (*.qss)")
            if _file == None: return
            if not _file.endswith('.qss'): _file += '.qss'
            self.lastSave = _file
            with open(_file, "w") as text_file:
                print(self.qssEditor.toPlainText()+'\n\n/* Created with DevTools QSS Editor */', file=text_file)

    class devTools(ts3plugin):
        name = "Developer Tools"
        requestAutoload = False
        version = "1.3"
        apiVersion = 21
        author = "Thomas \"PLuS\" Pathmann, Bluscream"
        description =  "Show information of the client's ui elements.\n"
        description += "Originally called widgetInfo.\n"
        description += "I enhanced this version a lot :)\n\n"
        description += "Features:\n"
        description += "- Browser like inspect element function\n"
        description += "- Test widget containing all possible UI elements to test styles\n"
        description += "- Runtime QSS Editor to view changes in realtime.\n"
        offersConfigure = False
        commandKeyword = ""
        infoTitle = None
        menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Inspect Element", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "QSS Editor", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "Test Widget", "")]
        hotkeys = [("info", "Inspect Element")]

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
            elif menuItemID == 1:
                self.edlg = qssDialog(self)
                self.edlg.show()
                self.edlg.raise_()
                self.edlg.activateWindow()
            elif menuItemID == 2:
                self.tdlg = TestDialog(self)
                self.tdlg.show()
                self.tdlg.raise_()
                self.tdlg.activateWindow()

except:
    print("Exception caught!")
