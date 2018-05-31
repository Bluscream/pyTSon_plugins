import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp, clientURL

class quickPerm(ts3plugin):
    name = "Quick Permissions"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Stolen from NoX by exp111"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [] # (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")
    hotkeys = []
    enabled = True
    permissions = [
        ("i_permission_modify_power", 75, True),
        ("i_client_permission_modify_power", 75, True),
        ("i_group_modify_power", 75, True),
        ("i_group_member_add_power", 75, True),
        ("b_virtualserver_token_add", True, True),
        ("b_virtualserver_token_list", True, True),
        ("b_virtualserver_token_use", True, True),
        ("b_virtualserver_token_delete", True, True),
        ("b_client_ignore_bans", True, True),
        ("b_client_remoteaddress_view", True, True)
    ]

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        self.enabled = not self.enabled
        ts3lib.printMessageToCurrentTab("{} set to [color=orange]{}".format(self.name,self.enabled))

    def onServerGroupClientAddedEvent(self, schid, clientID, clientName, clientUniqueIdentity, sgid, invokerClientID, invokerName, invokerUniqueIdentity):
        if not self.enabled: return
        if invokerClientID < 1: return
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID != clientID: return
        if invokerClientID == ownID: return
        (err, dgid) = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_SERVER_GROUP)
        if sgid == dgid: return
        (err, cldbid) = ts3lib.getClientVariable(schid, ownID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        for perm in self.permissions:
            (err, pid) = ts3lib.getPermissionIDByName(schid, perm[0])
            v = 100 if sgid == 2 and perm[1] == 75 else perm[1]
            ts3lib.requestClientAddPerm(schid, cldbid, [pid], [v], [perm[2]], "quickperm")
            (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
            ts3lib.requestChannelClientAddPerm(schid, ownCID, cldbid, [pid], [v], "quickperm")
            ts3lib.requestChannelAddPerm(schid, ownCID, [pid], v, "quickperm")

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode == "quickperm": return True
    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        if returnCode == "quickperm": return True