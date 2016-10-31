from ts3plugin import ts3plugin, PluginHost
import sys

class testhelper(ts3plugin):
    name = "testhelper"
    apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Thomas \"PLuS\" Pathmann"
    description = "Just a helper to test pyTSon"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []


    def __init__(self):
        #keep in mind, that this plugin won't show as enabled on client startup
        PluginHost.configure(None)
        ts3.printMessageToCurrentTab(str(sys.version_info))
