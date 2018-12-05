import ts3lib, csv
from os import path
from ts3defines import *
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from PythonQt.QtCore import QTimer
from bluscream import timestamp, clientURL, boolean, getScriptPath

class quickPerm(ts3plugin):
    path = getScriptPath(__name__)
    name = "Quick Permissions"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Stolen from NoX by exp111"
    offersConfigure = False
    commandKeyword = "perm"
    infoTitle = None
    menuItems = []
    hotkeys = []
    retcodes = {}
    perms = {} # "success": 0, "fail": 0, "processed": 0, "total": 0, "stop": False
    flood = False
    perms_essential = []
    perms_full = []
    permissions = [
        ("b_client_ignore_antiflood", True, True),
        ("i_permission_modify_power", 75, True),
        ("i_client_permission_modify_power", 75, True),
        ("i_group_modify_power", 75, True),
        ("i_channel_permission_modify_power", 75, True),
        ("i_group_member_add_power", 75, True),
        ("b_virtualserver_token_add", True, True),
        ("b_virtualserver_token_list", True, True),
        ("b_virtualserver_token_use", True, True),
        ("b_virtualserver_token_delete", True, True),
        ("b_client_ignore_bans", True, True),
        ("i_client_ban_power", 75, True),
        ("i_client_needed_ban_power", 75, True),
        ("b_client_remoteaddress_view", True, True),
        ("b_client_create_modify_serverquery_login", True, True),
        ("b_virtualserver_servergroup_permission_list", True, True),
        ("b_virtualserver_channelgroup_permission_list", True, True),
        ("b_virtualserver_client_permission_list", True, True),
        ("b_virtualserver_channel_permission_list", True, True),
        ("b_virtualserver_channelclient_permission_list", True, True)
    ]

    def __init__(self):
        with open(path.join(self.path, "essential.csv")) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row['Colour'] == 'blue':
                    print(row['ID'] ,row ['Make'],row ['Colour'])
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def processCommand(self, schid, keyword):
        perm = keyword.split(' ')
        print(len(perm), perm)
        # if len(perm) < 2: return False
        # if len(perm) == 2: perm.append(False).append(False)
        skip = perm[2] if len(perm) > 2 else False
        val = boolean(perm[1]) if len(perm) > 1 else True
        perm = perm[0]
        print(perm, val, skip)
        (err, clid) = ts3lib.getClientID(schid)
        (err, cldbid) = ts3lib.getClientVariable(schid, clid, ClientPropertiesRare.CLIENT_DATABASE_ID)
        (err, pid) = ts3lib.getPermissionIDByName(schid, perm)
        ts3lib.printMessageToCurrentTab("Requesting \"{}\" ({})".format(perm,pid))
        ts3lib.requestClientAddPerm(schid, cldbid, [pid], [val], [skip])
        (err, ownCID) = ts3lib.getChannelOfClient(schid, clid)
        ts3lib.requestChannelClientAddPerm(schid, ownCID, cldbid, [pid], [val])
        return True

    def onServerGroupClientAddedEvent(self, schid, clientID, clientName, clientUniqueIdentity, sgid, invokerClientID, invokerName, invokerUniqueIdentity):
        if invokerClientID < 1: return
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID != clientID: return
        if invokerClientID == ownID: return
        (err, dgid) = ts3lib.getServerVariable(schid, VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_SERVER_GROUP)
        if sgid == dgid: return
        self.getPerms(schid, clientID, sgid)

    def getPerms(self, schid, clid, sgid = 0):
        if self.flood: return
        (err, cldbid) = ts3lib.getClientVariable(schid, clid, ClientPropertiesRare.CLIENT_DATABASE_ID)
        self.perms = { "success": 0, "fail": 0, "processed": 0, "total": len(self.permissions), "stop": False}
        for perm in self.permissions:
            if self.perms["stop"]: break
            """
            if self.perms["fail"] > 0:
                self.perms = { "success": 0, "fail": 0, "processed": 0, "total": 0}; self.retcodes = {}
                ts3lib.printMessage(schid, "{} failed :(".format(self.name), ts3defines.PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
                break
            """
            (err, pid) = ts3lib.getPermissionIDByName(schid, perm[0])
            retcode = ts3lib.createReturnCode()
            self.retcodes[retcode] = perm[0]
            v = 100 if sgid == 2 and perm[1] == 75 else perm[1]
            ts3lib.requestClientAddPerm(schid, cldbid, [pid], [v], [perm[2]], retcode)
            (err, ownCID) = ts3lib.getChannelOfClient(schid, clid)
            if self.perms["stop"]: break
            ts3lib.requestChannelClientAddPerm(schid, ownCID, cldbid, [pid], [v], retcode)
            # ts3lib.requestChannelAddPerm(schid, ownCID, [pid], [v], "quickperm")

    def disableFlood(self): self.flood = False

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if not returnCode in self.retcodes: return False
        reason = "finished"; self.perms["processed"] += 1
        if error == ERROR_ok: self.perms["success"] += 1
        elif error == ERROR_client_is_flooding:
            self.perms["fail"] += 1; self.perms["stop"] = True;reason = "failed because of flooding"
        elif error in [ERROR_permissions_client_insufficient,ERROR_permissions_insufficient_group_power,ERROR_permissions_insufficient_permission_power]: self.perms["fail"] += 1
        # if self.perms["stop"]: self.retcodes = {}
        # else:
        del self.retcodes[returnCode]
        if not len(self.retcodes):
            ts3lib.printMessage(schid, "{} {} {}".format(self.name, reason, self.perms), PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
            if self.perms["stop"]: self.flood = True; QTimer.singleShot(5000, self.disableFlood)
        return True
"""
    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        if not returnCode in self.retcodes: return False
        print(self.name, "onServerPermissionErrorEvent")
        
        del self.retcodes[returnCode]
        return True
"""