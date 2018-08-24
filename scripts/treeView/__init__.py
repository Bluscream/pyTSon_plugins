import ts3defines, ts3lib, pytson
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from bluscream import timestamp, getScriptPath
from PythonQt.Qt import QApplication

def widget(name):
    instance = QApplication.instance()
    widgets = instance.allWidgets()
    del instance
    for x in widgets:
        if str(x.objectName) == name:
            return x

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
        ("tree_view_test", "Test")
    ]

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def processCommand(self, schid, keyword): self.onHotkeyOrCommandEvent(keyword, schid)
    def onHotkeyEvent(self, keyword): self.onHotkeyOrCommandEvent(keyword)
    def onHotkeyOrCommandEvent(self, keyword, schid=0):
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        if not keyword == "tree_view_test": return
        servertree = widget("ServerTreeView")
        print(dir(servertree))
        selected = servertree.selectedIndexes()[0]
        # print(self.name, "> selected:", selected)
        # print(self.name, "> dir(selected):", dir(selected))
        for item in dir(selected):
            if item.startswith("__"): continue
            if item in ["help"]: continue
            item = "selected.{}".format(item)
            var = eval(item)
            try:
                eval(item+"()")
                if callable(var):
                    item += "()"
            except: pass
            print(item+":", eval(item))
        # servertree.columnAt(selected.column())
        servertree.collapseAll()