import ts3defines, ts3lib, pytson
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from bluscream import timestamp, getScriptPath, widget
from PythonQt.Qt import QApplication

class spacify(ts3plugin):
    path = getScriptPath(__name__)
    name = "Spacify"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    widget = None
    last = ""
    # ignore = False


    def __init__(self):
        self.widget = widget("ChatLineEdit")
        result = self.widget.connect("textChanged()", self.textEdited)
        print("Result", result)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def stop(self):
        self.widget.disconnect("textChanged()", self.textEdited)

    def textEdited(self):
        text = self.widget.toPlainText()
        if not text.endswith(" "):
            self.widget.insert(" ")
            # self.widget.cursorPosition(len(text)+1)
            # self.ignore = True
        self.last = self.widget.toPlainText()