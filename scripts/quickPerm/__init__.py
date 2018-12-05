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
    perms = {} # "success": 0, "fail": 0, "processed": 0, "stop": False
    flood = False
    p = ()

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def processCommand(self, schid, keyword):
        args = keyword.split(' ')
        cmd = args.pop(0).lower()
        (err, clid) = ts3lib.getClientID(schid)
        (err, cldbid) = ts3lib.getClientVariable(schid, clid, ClientPropertiesRare.CLIENT_DATABASE_ID)
        if cmd == "grant":
            # if len(perm) < 2: return False
            # if len(perm) == 2: perm.append(False).append(False)
            skip = args[2] if len(args) > 2 else False
            val = boolean(perm[1]) if len(args) > 1 else True
            perm = args[0]
            (err, pid) = ts3lib.getPermissionIDByName(schid, perm)
            ts3lib.printMessageToCurrentTab("Requesting \"{}\" ({})".format(perm,pid))
            ts3lib.requestClientAddPerm(schid, cldbid, [pid], [val], [skip])
            (err, ownCID) = ts3lib.getChannelOfClient(schid, clid)
            ts3lib.requestChannelClientAddPerm(schid, ownCID, cldbid, [pid], [val])
        elif cmd == "essential": self.getPerms(schid)
        elif cmd == "full": self.getFullPerms(schid)
        elif cmd == "build":
            _file = args.pop(0)
            self.p = self.buildLists(path.join(self.path, "{}.csv".format(_file)), schid)
            length = len(self.p[0])
            print("ids",length,"vals",len(self.p[1]),"skips",len(self.p[2]),"negates",len(self.p[3]))
            print("\nIDs:\n",self.p[0]);print("\nvals:\n",self.p[1]);print("\nskips:\n",self.p[2]);print("\nnegates:\n",self.p[3])
            ts3lib.printMessageToCurrentTab("Loaded {} permissions".format(length))
        elif cmd == "client":
            each = len(args)
            if not each: ts3lib.requestClientAddPerm(schid, cldbid, self.p[0], self.p[1], self.p[2])
            else:
                length = len(self.p[0])
                for x in range(length):
                    ts3lib.requestClientAddPerm(schid, cldbid, [self.p[0][x]], [self.p[1][x]], [self.p[2][x]])
        elif cmd in ["channelclient","clientchannel"]:
            (err, ownCID) = ts3lib.getChannelOfClient(schid, clid)
            each = len(args)
            if not each: ts3lib.requestChannelClientAddPerm(schid, ownCID, cldbid, self.p[0], self.p[1])
            else:
                length = len(self.p[0])
                for x in range(length):
                    ts3lib.requestChannelClientAddPerm(schid, ownCID, cldbid, [self.p[0][x]], [self.p[1][x]])

        elif cmd == "channel":
            (err, ownCID) = ts3lib.getChannelOfClient(schid, clid)
            ts3lib.ts3lib.requestChannelAddPerm(schid, ownCID, self.p[0], self.p[1])
        elif cmd == "sgroup":
            sgid = int(args.pop(0))
            ts3lib.requestServerGroupAddPerm(schid, sgid, 1, self.p[0], self.p[1], self.p[2], self.p[3])
        elif cmd == "cgroup":
            cgid = int(args.pop(0))
            ts3lib.requestChannelGroupAddPerm(schid, cgid, 1, self.p[0], self.p[1])
        elif cmd == "id":
            (err, pid) = ts3lib.getPermissionIDByName(schid, args[0])
            ts3lib.printMessageToCurrentTab("{} = [b]{}".format(args[0], pid))
        else: return False
        return True

    def onServerGroupClientAddedEvent(self, schid, clientID, clientName, clientUniqueIdentity, sgid, invokerClientID, invokerName, invokerUniqueIdentity):
        if invokerClientID < 1: return
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID != clientID: return
        # if invokerClientID == ownID: return
        (err, dgid) = ts3lib.getServerVariable(schid, VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_SERVER_GROUP)
        if sgid == dgid: return
        self.getPerms(schid, clientID, sgid)
        # for sgid in [167,169,165]:
            # ts3lib.requestServerGroupAddPerm(schid, sgid, 1, [166], [75], [0], [0])

    def getPerms(self, schid, clid = 0, sgid = 0):
        if self.flood: return
        if not clid: (err, clid) = ts3lib.getClientID(schid)
        (err, cldbid) = ts3lib.getClientVariable(schid, clid, ClientPropertiesRare.CLIENT_DATABASE_ID)
        self.perms = { "success": 0, "fail": 0, "processed": 0, "stop": False}
        with open(path.join(self.path, "essential.csv")) as csvfile:
            permissions = csv.reader(csvfile, delimiter=';')
            for perm in permissions:
                if self.perms["stop"]: break
                (err, pid) = ts3lib.getPermissionIDByName(schid, perm[0])
                retcode = ts3lib.createReturnCode()
                self.retcodes[retcode] = perm[0]
                v = 100 if sgid == 2 and perm[1] == "75" else int(perm[1])
                ts3lib.requestClientAddPerm(schid, cldbid, [pid], [v], [int(perm[2])], retcode)
                (err, ownCID) = ts3lib.getChannelOfClient(schid, clid)
                if self.perms["stop"]: break
                ts3lib.requestChannelClientAddPerm(schid, ownCID, cldbid, [pid], [v], retcode)
                # ts3lib.requestChannelAddPerm(schid, ownCID, [pid], [v], "quickperm")

    def getFullPerms(self, schid):
        (err, clid) = ts3lib.getClientID(schid)
        (err, cldbid) = ts3lib.getClientVariable(schid, clid, ClientPropertiesRare.CLIENT_DATABASE_ID)
        with open(path.join(self.path, "full.csv")) as csvfile:
            perms_full = csv.reader(csvfile, delimiter=';')
            for perm in perms_full:
                (err, pid) = ts3lib.getPermissionIDByName(schid, perm[0])
                ts3lib.requestClientAddPerm(schid, cldbid, [pid], [int(perm[1])], [int(perm[2])])

    def disableFlood(self): self.flood = False

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        if not returnCode in self.retcodes: return False
        reason = "finished"; self.perms["processed"] += 1
        if error == ERROR_ok:
            self.perms["success"] += 1
        elif error == ERROR_client_is_flooding:
            self.perms["fail"] += 1; self.perms["stop"] = True;reason = "failed because of flooding"
        elif error in [ERROR_permissions_client_insufficient,ERROR_permissions_insufficient_group_power,ERROR_permissions_insufficient_permission_power]: self.perms["fail"] += 1
        # if self.perms["stop"]: self.retcodes = {}
        # else:
        del self.retcodes[returnCode]
        if not len(self.retcodes):
            ts3lib.printMessage(schid, "{} {} {}".format(self.name, reason, self.perms), PluginMessageTarget.PLUGIN_MESSAGE_TARGET_SERVER)
            if self.perms["stop"]: self.flood = True; QTimer.singleShot(5000, self.disableFlood)
            elif self.perms["success"] > 0: self.getFullPerms(schid)
        return True

    def buildLists(self, file, schid=0):
        ids=[];vals=[];skips=[];negates=[];grants=[]
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        with open(file) as csvfile:
            permissions = csv.DictReader(csvfile, delimiter=';', fieldnames=["Name","Value","Skip","Negate","Grant"])
            for perm in permissions:
                # if not perm[0].startsWith("i_"): continue
                (err, pid) = ts3lib.getPermissionIDByName(schid, perm["Name"])
                if err != ERROR_ok: continue
                ids.append(pid)
                val = int(perm["Value"]) if perm["Value"] else 0
                vals.append(val)
                skip = int(perm["Skip"]) if perm["Value"] else 0
                skips.append(skip)
                neg = int(perm["Negate"]) if perm["Negate"] else 0
                negates.append(neg)
                grant = int(perm["Value"]) if perm["Value"] else 0
                if (grant):
                    grantid = perm["Name"].replace("i_", "i_needed_modify_power_").replace("b_", "b_needed_modify_power_")
                    grants.append((grantid, grant))
        for perm in grants:
            (err, pid) = ts3lib.getPermissionIDByName(schid, perm[0])
            if err != ERROR_ok: continue
            ids.append(pid)
            vals.append(perm[1])
            skips.append(0)
            negates.append(0)
        return (ids, vals, skips, negates)