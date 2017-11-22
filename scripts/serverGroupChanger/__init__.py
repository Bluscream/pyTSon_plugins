import ts3defines, ts3lib
from pytson import getPluginPath
from ts3plugin import ts3plugin
from os import path
from datetime import datetime

class serverGroupChanger(ts3plugin):
    name = "Server Group Changer"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Requested by mrcraigtunstall"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Toggle Group 1", ""),
				(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 1, "Toggle Group 2", "")]
    hotkeys = []
    debug = False
    sgid1 = 1
    sgid2 = 2


    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            (err, dbid) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
            (err, sgroups) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
            if menuItemID == 0:
                if self.sgid1 in sgroups: ts3lib.requestServerGroupDelClient(schid, self.sgid1, dbid)
                else: ts3lib.requestServerGroupAddClient(schid, self.sgid1, dbid)
            elif menuItemID == 1:
                if self.sgid2 in sgroups: ts3lib.requestServerGroupDelClient(schid, self.sgid2, dbid)
                else: ts3lib.requestServerGroupAddClient(schid, self.sgid2, dbid)
