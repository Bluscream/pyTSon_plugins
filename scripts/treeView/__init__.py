import ts3defines, ts3lib, pytson
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from bluscream import timestamp, getScriptPath, getIDByName
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
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        self.servertree = self.widget("ServerTreeView")
        # print(self.name, "> servertree:", self.servertree)
        selected = self.servertree.selectedIndexes()[0]
        # print(self.name, "> selected:", selected)
        name = selected.data()
        item = getIDByName(name, schid)
        if keyword == "tree_view_selected_name":
            # print(self.name, "> dir(selected):", dir(selected))
            ts3lib.printMessageToCurrentTab("[b]Selected Item: \"{}\"\nType: {} ID: {}".format(name, item[1], item[0]))
            # print(self.name, "> selected.flags():", selected.flags())
            # print(self.name, "> selected.internalId():", selected.internalId())
            # print(self.name, "> selected.internalPointer():", selected.internalPointer())
            # print(self.name, "> selected.row():", selected.row())
        elif keyword == "tree_view_message_selected":
            msg = "lol i found you!"
            if item[1] == ServerTreeItemType.SERVER:
                ts3lib.requestSendServerTextMsg(schid, msg)
            elif item[1] == ServerTreeItemType.CHANNEL:
                ts3lib.requestSendChannelTextMsg(schid, msg, item[0])
            elif item[1] == ServerTreeItemType.CLIENT:
                ts3lib.requestSendPrivateTextMsg(schid, msg, item[0])