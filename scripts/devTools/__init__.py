import ts3lib as ts3; from ts3plugin import ts3plugin
from pytsonui import setupUi
from PythonQt.QtGui import QApplication, QCursor, QDialog, QSplitter, QTreeView, QTableView, QHBoxLayout, QVBoxLayout, QCheckBox, QWidget, QItemSelectionModel, QMenu, QMessageBox, QFileDialog, QTextDocument
from PythonQt.QtCore import Qt, QAbstractItemModel, QModelIndex
import ts3lib as ts3; import   ts3defines, os

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
            self.setWindowTitle('Inspect Element : : Developer Tools')

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
            else:
                obj.setEnabled(True)


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
            chatWidget = self.getWidgetByObjectName("ChatTab")
            self.chatsheet = chatWidget.findChild(QTextDocument).defaultStyleSheet
            self.html = self.getWidgetByObjectName("InfoFrame").html
            self.chat_html = chatWidget.findChild("QWidgetTextControl").html
            self.qssEditor.setPlainText(self.stylesheet)
            self.chatEditor.setPlainText(self.chatsheet)
            self.tplEditor.setPlainText(self.html)
            self.chatEditor_html.setPlainText(self.chat_html)
            self.chatEditor.setReadOnly(True);self.tplEditor.setReadOnly(True)
            index = self.tabWidget.currentIndex
            if index == 0:
                self.btn_apply.setEnabled(True);self.btn_minify.setEnabled(True);self.btn_insert.setEnabled(True);self.btn_reset.setEnabled(True);self.chk_live.setEnabled(True)
            elif index == 1:
                self.btn_apply.setEnabled(False);self.btn_minify.setEnabled(True);self.btn_insert.setEnabled(False);self.btn_reset.setEnabled(False);self.chk_live.setEnabled(False)
            else:
                self.btn_apply.setEnabled(False);self.btn_minify.setEnabled(False);self.btn_insert.setEnabled(False);self.btn_reset.setEnabled(False);self.chk_live.setEnabled(False)
            self.lastSave = None
        def getWidgetByObjectName(self, name):
            QApp = QApplication.instance()
            widgets = QApp.topLevelWidgets()
            widgets += QApp.allWidgets()
            for x in widgets:
                if str(x.objectName) == name: return x
        def getWidgetByClassName(self, name):
            QApp = QApplication.instance()
            widgets = QApp.topLevelWidgets()
            widgets += QApp.allWidgets()
            for x in widgets:
                if str(x.__class__) == name: return x
        def on_tabWidget_currentChanged(self, index):
            #ts3.printMessageToCurrentTab(str(index))
            #if self.tabWidget.findChild(QPlainTextEdit).isReadOnly():
            if index == 0:
                self.btn_apply.setEnabled(True);self.btn_minify.setEnabled(True);self.btn_insert.setEnabled(True);self.btn_reset.setEnabled(True);self.chk_live.setEnabled(True)
            elif index == 1:
                self.btn_apply.setEnabled(False);self.btn_minify.setEnabled(True);self.btn_insert.setEnabled(False);self.btn_reset.setEnabled(False);self.chk_live.setEnabled(False)
            else:
                self.btn_apply.setEnabled(False);self.btn_minify.setEnabled(False);self.btn_insert.setEnabled(False);self.btn_reset.setEnabled(False);self.chk_live.setEnabled(False)
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
            i = self.tabWidget.currentIndex
            if i == 0:
                QApplication.instance().styleSheet = self.qssEditor.toPlainText()
            elif i == 1:
                QApp = QApplication.instance()
                widgets = QApp.topLevelWidgets() + QApp.allWidgets()
                for x in widgets:
                    if x.objectName == "ChatTab":
                        x.findChild(QTextDocument).defaultStyleSheet = self.chatEditor.toPlainText()
            elif i == 2:
                _i = self.getWidgetByObjectName("InfoFrame")
                _o = _i.styleSheet
                _i.styleSheet = "background:red;"
                _i.html = self.html
                _i.styleSheet = _o
        def on_btn_insert_clicked(self):
            self.qssEditor.appendPlainText("\n{\n\t:\n}")
        def on_btn_reset_clicked(self):
            if QMessageBox(QMessageBox.Warning, "Reset QSS?", "This will reset your changes to the initial Stylesheet! Continue?", QMessageBox.Ok | QMessageBox.Cancel).exec_() == QMessageBox.Ok:
                QApplication.instance().styleSheet = self.stylesheet
                self.qssEditor.setPlainText(self.stylesheet)
        def on_btn_minify_clicked(self):
            try:
                try:
                      from css_html_js_minify import css_minify
                except:
                      _t = QMessageBox.question(self, "Can't minify", "Python package \"css_html_js_minify\" could not be loaded.\nDo you want to try installing it now?", QMessageBox.Yes, QMessageBox.No)
                      if _t == QMessageBox.Yes:
                          from devtools import PluginInstaller
                          PluginInstaller().installPackages(['css_html_js_minify'])
                          self.on_btn_minify_clicked()
                      return
                      #import traceback; QMessageBox.Critical("Can't minify", traceback.format_exc()).exec_()
                index = self.tabWidget.currentIndex
                _old = ""
                if index == 0:
                    _old = self.qssEditor.toPlainText()
                elif index == 1: _old = self.chatEditor.toPlainText()
                _minified = css_minify(_old,noprefix=True) # , encode=False
                if index == 0:
                    QApplication.instance().styleSheet = _minified
                    self.qssEditor.setPlainText(_minified)
                elif index == 1: self.chatEditor.setPlainText(_minified);return
                if QMessageBox(QMessageBox.Warning, "Use minified QSS?", "Your minified QSS code has been applied.\n\nIf you encounter any issues with the minified code you should click on cancel.", QMessageBox.Ok | QMessageBox.Cancel).exec_() == QMessageBox.Cancel:
                    QApplication.instance().styleSheet = _old
                    self.qssEditor.setPlainText(_old)
            except:
                try:
                    from traceback import format_exc
                    QMessageBox(QMessageBox.Critical, "Can't minify", format_exc()).exec_()
                except:
                    print(format_exc())
        def on_btn_beautify_clicked(self):
            try:
                try:
                    from bs4 import BeautifulSoup
                except Exception:
                    from traceback import format_exc
                    print("Error: {0}".format(format_exc()))
                    _t = QMessageBox.question(self, "Can't beautify", "Python package \"beautifulsoup4\" could not be loaded.\nDo you want to try installing it now?", QMessageBox.Yes, QMessageBox.No)
                    if _t == QMessageBox.Yes:
                      from devtools import PluginInstaller
                      PluginInstaller().installPackages(['beautifulsoup4'])
                      self.on_btn_beautify_clicked()
                    return
                    #import traceback; QMessageBox.Critical("Can't minify", traceback.format_exc()).exec_()
                index = self.tabWidget.currentIndex
                _old = ""
                if index == 0: _old = self.qssEditor.toPlainText()
                elif index == 1: _old = self.chatEditor.toPlainText()
                elif index == 2: _old = self.tplEditor.toPlainText()
                elif index == 3: _old = self.chatEditor_html.toPlainText()
                _beautified = BeautifulSoup(_old)
                _beautified = _beautified.prettify()
                if index == 0:
                    QApplication.instance().styleSheet = _beautified
                    self.qssEditor.setPlainText(_beautified)
                elif index == 1: self.chatEditor.setPlainText(_beautified);return
                elif index == 2: self.tplEditor.setPlainText(_beautified);return
                elif index == 3: self.chatEditor_html.setPlainText(_beautified);return
                if QMessageBox(QMessageBox.Warning, "Use beautified code?", "Your beautified code has been applied.\n\nIf you encounter any issues with the beautified code you should click on cancel.", QMessageBox.Ok | QMessageBox.Cancel).exec_() == QMessageBox.Cancel:
                    QApplication.instance().styleSheet = _old
                    self.qssEditor.setPlainText(_old)
            except:
                try:
                    from traceback import format_exc
                    QMessageBox(QMessageBox.Critical, "Can't beautify", format_exc()).exec_()
                except:
                    print(format_exc())

        def on_btn_save_clicked(self):
            _file = None;_ext = "";_text = ""
            i = self.tabWidget.currentIndex
            if i == 0:
                _ext = '.qss';_text = self.qssEditor.toPlainText()+'\n\n/* Created with DevTools QSS Editor */'
            elif i == 1:
                _ext = '.qss';_text = self.chatEditor.toPlainText()+'\n\n/* Created with DevTools QSS Editor */'
            elif i == 2:
                _ext = '.tpl';_text = self.tplEditor.toPlainText()+'\n\n<!-- Created with DevTools QSS Editor -->'
            if self.lastSave:
                _file = QFileDialog.getSaveFileName(self, "Save Qt Stylesheet", self.lastSave, "Teamspeak 3 Stylesheet File (*"+_ext+")")
            else:
                _file = QFileDialog.getSaveFileName(self, "Save Qt Stylesheet", "", "Teamspeak 3 Stylesheet File (*"+_ext+")")
            if _file == None: return
            if not _file.endswith(_ext): _file += _ext
            self.lastSave = _file
            with open(_file, "w") as text_file:
                print(_text, file=text_file)

    class devTools(ts3plugin):
        name = "Developer Tools"
        requestAutoload = False
        version = "1.3"
        apiVersion = 22
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
