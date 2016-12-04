from ts3plugin import ts3plugin, PluginHost

class profile(ts3plugin):
    name = "Profile"
    apiVersion = 20
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Share your info"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []


    def __init__(self):
        PluginHost.configure(None)
