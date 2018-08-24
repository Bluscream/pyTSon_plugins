import ts3defines, ts3lib, pytson
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from bluscream import timestamp, getScriptPath, getIDByName, getChannelPassword
from ts3enums import ServerTreeItemType
from PythonQt.Qt import QApplication

class treeView(ts3plugin):
    path = getScriptPath(__name__)
    name = "Tree View Test"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "tv"
    infoTitle = None
    menuItems = []
    hotkeys = [
        ("tree_view_selected_name", "Print Selected name to current tab"),
        ("tree_view_message_selected", "Message selected client, channel or server")
    ]
    app = QApplication.instance()
    servertree = None

    def widget(self, name):
        widgets = self.app.allWidgets()
        for x in widgets:
            if str(x.objectName) == name:
                return x

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def processCommand(self, schid, keyword): self.onHotkeyOrCommandEvent(keyword, schid)
    def onHotkeyEvent(self, keyword): self.onHotkeyOrCommandEvent(keyword)
    def onHotkeyOrCommandEvent(self, keyword, schid=0):
        if not self.app.activeWindow().className() == "MainWindow": return
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        self.servertree = self.widget("ServerTreeView")
        # print(self.name, "> servertree:", self.servertree)
        selected = self.servertree.currentIndex()
        if not selected: return
        # print(self.name, "> selected:", selected)
        name = selected.data()
        item = getIDByName(name, schid)
        if keyword == "tree_view_selected_name":
            # print(self.name, "> dir(selected):", dir(selected))
            # print(self.name, "> selected.flags():", selected.flags())
            # print(self.name, "> selected.internalId():", selected.internalId())
            # print(self.name, "> selected.internalPointer():", selected.internalPointer())
            # print(self.name, "> selected.row():", selected.row())
            ts3lib.printMessageToCurrentTab("[b]Selected Item: \"{}\"\nType: {} ID: {}".format(name, item[1], item[0]))
        elif keyword == "tree_view_message_selected":
            msg = " "
            if item[1] == ServerTreeItemType.SERVER:
                ts3lib.requestSendServerTextMsg(schid, msg)
            elif item[1] == ServerTreeItemType.CHANNEL:
                (err, clid) = ts3lib.getClientID(schid)
                (err, cid) = ts3lib.getChannelOfClient(schid, clid)
                if cid != item[0]:
                    pw = getChannelPassword(schid, item[0])
                    ts3lib.printMessageToCurrentTab("{} > PW: {}".format(self.name, pw))
                    err = ts3lib.requestClientMove(schid, clid, item[0], pw if pw else "123")
                if not err: ts3lib.requestSendChannelTextMsg(schid, msg, 0)
            elif item[1] == ServerTreeItemType.CLIENT:
                ts3lib.requestSendPrivateTextMsg(schid, msg, item[0])
        elif keyword == "tree_view_enter_channel":
            if item[1] != ServerTreeItemType.CHANNEL: return
            (err, clid) = ts3lib.getClientID(schid)
            (err, cid) = ts3lib.getChannelOfClient(schid, clid)
            if cid == item[0]: return
            pw = getChannelPassword(schid, item[0])
            ts3lib.printMessageToCurrentTab("{} > PW: {}".format(self.name, pw))
            ts3lib.requestClientMove(schid, clid, item[0], pw if pw else "123")