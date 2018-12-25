from ts3plugin import ts3plugin

import ts3defines, pytson, ts3client
import os
from configparser import ConfigParser

from PythonQt.QtGui import QDialog, QHBoxLayout, QVBoxLayout, QTreeView, QSortFilterProxyModel, QPushButton, QToolButton, QSpacerItem, QSizePolicy, QSpinBox, QLabel, QLineEdit, QIcon
from PythonQt.QtCore import Qt, QAbstractItemModel, QModelIndex

class EventlogModel(QAbstractItemModel):
    def __init__(self, parent):
        super().__init__(parent)

        self._maxevents = 100
        self._paused = False
        self.events = []
        self.pevents = []

    def pause(self):
        self._paused = True

    def unpause(self):
        self.beginResetModel()
        self.events = (self.events + self.pevents)[-self._maxevents:]
        self.pevents = []
        self._paused = False
        self.endResetModel()

    @property
    def maximumEvents(self):
        return self._maxevents

    @maximumEvents.setter
    def maximumEvents(self, val):
        if val < 0:
            val = 0

        self._maxevents = val

        if val != 0 and len(self.events) > val:
            idx = len(self.events) - val
            self.beginRemoveRows(QModelIndex(), 0, idx)
            self.events = self.events[idx:]
            self.endRemoveRows()

    def callback(self, name, *args):
        if self._paused:
            self.pevents.append((name, args))
            return

        if self._maxevents != 0 and len(self.events) >= self._maxevents:
            self.beginRemoveRows(QModelIndex(), 0, len(self.events) - self._maxevents)
            self.events = self.events[len(self.events) - self._maxevents +1:]
            self.endRemoveRows()

        idx = len(self.events)
        self.beginInsertRows(QModelIndex(), idx, idx)
        self.events.append((name, args))
        self.endInsertRows()

    def index(self, row, column, parent):
        if not parent.isValid():
            return self.createIndex(row, column, 0)
        else:
            return self.createIndex(row, column, parent.row() +1)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        if index.internalId() == 0:
            return QModelIndex()
        else:
            return self.createIndex(index.internalId() -1, 0, 0)

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.events)
        elif parent.internalId() == 0:
            if len(self.events[parent.row()][1]) > 0:
                return 1
            else:
                return 0
        else:
            return 0

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        if role == Qt.DisplayRole:
            if index.parent().isValid():
                return ", ".join(map(str, self.events[index.parent().row()][1]))
            else:
                return self.events[index.row()][0]
        elif role == Qt.UserRole:
            #the proxymodel use this role to filter, so child items won't be filtered out
            if index.parent().isValid():
                return self.events[index.internalId() -1][0]
            else:
                return self.events[index.row()][0]
        else:
            return None

class EventlogDialog(QDialog):
    def __init__(self, cfg, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Eventlog")

        self.cfg = cfg

        self.pauseButton = QPushButton("Pause", self)
        self.pauseButton.setCheckable(True)
        self.pauseButton.connect("toggled(bool)", self.onPauseButtonToggled)
        self.spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.maxLabel = QLabel("Maximum Events:", self)
        self.maxSpin = QSpinBox(self)
        self.maxSpin.setMaximum(10000)
        self.maxSpin.setToolTip("Set to 0 to not shrink events at all")
        self.maxSpin.setValue(cfg.getint("maximumEvents"))
        self.maxSpin.connect("valueChanged(int)", self.onMaxSpinChanged)

        self.sublay1 = QHBoxLayout()
        self.sublay1.addWidget(self.pauseButton)
        self.sublay1.addItem(self.spacer)
        self.sublay1.addWidget(self.maxLabel)
        self.sublay1.addWidget(self.maxSpin)

        self.filterLabel = QLabel("Filter:", self)
        self.filterEdit = QLineEdit(self)
        self.filterEdit.connect("textChanged(QString)", self.onFilterEditChanged)
        self.filterButton = QToolButton(self)
        self.filterButton.connect("clicked()", self.filterEdit.clear)
        try:
            ico = ts3client.IconPack.current()
            ico.open()
            self.filterButton.setIcon(QIcon(ico.icon("ERROR")))
            ico.close()
        except Exception as e:
            self.filterButton.setText("X")

        self.sublay2 = QHBoxLayout()
        self.sublay2.addWidget(self.filterLabel)
        self.sublay2.addWidget(self.filterEdit)
        self.sublay2.addWidget(self.filterButton)

        self.model = EventlogModel(self)
        self.model.maximumEvents = cfg.getint("maximumEvents")
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setFilterRole(Qt.UserRole)
        self.proxy.setSourceModel(self.model)

        self.tree = QTreeView(self)
        self.tree.header().hide()
        self.tree.setModel(self.proxy)

        self.lay = QVBoxLayout(self)
        self.lay.addLayout(self.sublay1)
        self.lay.addLayout(self.sublay2)
        self.lay.addWidget(self.tree)

        self.resize(cfg.getint("width"), cfg.getint("height"))

        self.connect("finished(int)", self.onFinished)

    def onMaxSpinChanged(self, val):
        self.model.maximumEvents = val
        self.cfg["maximumEvents"] = str(val)

    def onFilterEditChanged(self, txt):
        self.proxy.setFilterRegExp(txt)

    def onPauseButtonToggled(self, checked):
        if checked:
            self.model.pause()
        else:
            self.model.unpause()

    def onFinished(self, result):
        self.cfg["width"] = str(self.width)
        self.cfg["height"] = str(self.height)

    def callback(self, name, *args):
        self.model.callback(name, *args)

class eventlog(ts3plugin):
    requestAutoload = False
    name = "eventlog"
    version = "1.0.0"
    apiVersion = 21
    author = "Thomas \"PLuS\" Pathmann"
    description = "This plugin shows all available events in a log. Might be helpfull for plugin deveolopers."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Eventlog", os.path.join("ressources", "octicons", "list-unordered.svg.png"))]
    hotkeys = []

    def __init__(self):
        self.log = None
        self.cfg = ConfigParser()

        #set default values
        self.cfg.add_section("general")
        self.cfg.set("general", "maximumEvents", "100")
        self.cfg.set("general", "height", "200")
        self.cfg.set("general", "width", "350")

        cfgpath = pytson.getConfigPath("eventlog.conf")
        if os.path.isfile(cfgpath):
            self.cfg.read(cfgpath)

    def stop(self):
        with open(pytson.getConfigPath("eventlog.conf"), "w") as f:
            self.cfg.write(f)

    def showLog(self, parent):
        if not self.log:
            self.log = EventlogDialog(self.cfg["general"], parent)

        self.log.show()
        self.log.raise_()
        self.log.activateWindow()

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.showLog(None)

    def menuCreated(self):
        pass #just here to not be triggered in __getattr__

    def callback(self, name, *args):
        if self.log:
            self.log.callback(name, *args)

    def __getattr__(self, name):
        return (lambda *args: self.callback(name, *args))
