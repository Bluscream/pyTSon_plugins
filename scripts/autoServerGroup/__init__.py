import ts3lib, ts3defines, re
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from datetime import datetime
from bluscream import timestamp, sendCommand, inputBox, intList

class autoServerGroup(ts3plugin):
    name = "Auto Server Group"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "disconnect"
    infoTitle = None
    menuItems = []
    hotkeys = []
    added = 0
    clid = 0
    sgids = [28,27,26,21,17,16,9]
    sgid = 83
    description = "{:%d.%m %H:%M:%S} | {invokerName}"

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onServerGroupClientAddedEvent(self, schid, clid, clientName, clientUniqueIdentity, sgid, invokerClientID, invokerName, invokerUniqueIdentity):
        if sgid in self.sgids:
            err, description = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_DESCRIPTION)
            print("description:", description)
            if re.match(".*\d\d.\d\d \d\d:\d\d:\d\d | .*", description): return
            description = "{} {}".format(description, self.description.format(datetime.now(),invokerName=invokerName))
            ts3lib.requestClientEditDescription(schid, clid, description)
    def onServerGroupClientDeletedEvent(self, schid, clid, clientName, clientUniqueIdentity, sgid, invokerClientID, invokerName, invokerUniqueIdentity):
        err, sgids = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        print("Servergroups",sgids)
        sgids = intList(sgids)
        if any(x in self.sgids for x in sgids):
            print("true")

    def onUpdateClientEvent(self, schid, clid, invokerID, invokerName, invokerUniqueIdentifier):
        if clid != self.clid: return
        self.clid = 0
        err, description = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_DESCRIPTION)
        description = "{} {}: {}".format(description, timestamp(), invokerID)
        ts3lib.requestClientEditDescription(schid, clid, description)
