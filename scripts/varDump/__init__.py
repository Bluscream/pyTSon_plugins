from ts3plugin import ts3plugin
from bluscream import clientURL
import ts3lib, ts3defines, ts3enums

class varDump(ts3plugin):
    name = "Dump Variables"
    requestAutoload = True
    version = "1.0"
    apiVersion = 21
    author = "Bluscream"
    description = "This is a testplugin"
    offersConfigure = False
    commandKeyword = "var"
    infoTitle = ""
    menuItems = []
    hotkeys = []
    filepath = "vars.txt"
    req = 0
    retcode = "";schid = 0

    def __init__(self):
        pass

    def onIncomingClientQueryEvent(self, schid, commandText):
        if not schid == self.schid and not self.retcode: return
        self.retcode = "";self.schid = 0
        ts3lib.printMessageToCurrentTab(commandText)

    # 2018-12-23 18:44:16.901684|CRITICAL|Variables     |   |checkItemIndexValid() on unregistered variable | Index:64
    # noinspection PyArgumentList,PyTypeChecker
    def processCommand(self, schid, keyword):
        args = keyword.split()
        cmd = args.pop(0).lower()
        if cmd == "com":
            command = " ".join(args)
            self.retcode = ts3lib.createReturnCode(); self.schid = schid
            err = ts3lib.requestSendClientQueryCommand(schid, command, self.retcode)
            if err != ts3defines.ERROR_ok:
                (_err, msg) = ts3lib.getErrorMessage(err)
                ts3lib.printMessageToCurrentTab("(%s) %s: %s"%(schid, command, msg))
        elif cmd == "req":
            clid = int(args.pop(0))
            self.req = clid
            ts3lib.requestClientVariables(schid, clid)
        elif cmd == "reqcon":
            clid = int(args.pop(0))
            self.req = clid
            ts3lib.requestConnectionInfo(schid, clid)
        elif cmd == "self":
            err, clid = ts3lib.getClientID(schid)
            ts3lib.printMessageToCurrentTab("[b]{}'s Self Variables:".format(clientURL(schid, clid)))
            open(self.filepath, 'w').close()
            min=0;max=64
            if len(args):
                min = int(args.pop(0))
                if len(args): max = int(args.pop(0))
            for i in range(min, max):
                msg = "%s"%i
                values = set(item.value for item in ts3enums.ClientProperties)
                if i in values: msg += " ({})".format(ts3enums.ClientProperties(i))
                msg += ": "
                (err, var) = ts3lib.getClientSelfVariableAsString(schid, i)
                if err != ts3defines.ERROR_ok:
                    (_err, var) = ts3lib.getErrorMessage(err)
                msg += var
                with open(self.filepath, "a", encoding="utf-8") as myfile:
                    myfile.write(msg+"\n")
                ts3lib.printMessageToCurrentTab(msg)
        elif cmd == "client":
            clid = int(args.pop(0))
            ts3lib.printMessageToCurrentTab("[b]{}'s Client Variables:".format(clientURL(schid, clid)))
            open(self.filepath, 'w').close()
            min=0;max=64
            if len(args):
                min = int(args.pop(0))
                if len(args): max = int(args.pop(0))
            for i in range(min, max):
                msg = "%s"%i
                values = set(item.value for item in ts3enums.ClientProperties)
                if i in values: msg += " ({})".format(ts3enums.ClientProperties(i))
                msg += ": "
                (err, var) = ts3lib.getClientVariableAsString(schid, clid, i)
                if err != ts3defines.ERROR_ok:
                    (_err, var) = ts3lib.getErrorMessage(err)
                msg += var
                with open(self.filepath, "a", encoding="utf-8") as myfile:
                    myfile.write(msg+"\n")
                ts3lib.printMessageToCurrentTab(msg)
        elif cmd == "con":
            clid = int(args.pop(0))
            ts3lib.printMessageToCurrentTab("[b]{}'s Connection Variables:".format(clientURL(schid, clid)))
            open(self.filepath, 'w').close()
            min=0;max=65
            if len(args):
                min = int(args.pop(0))
                if len(args): max = int(args.pop(0))
            for i in range(min, max):
                msg = "%s"%i
                values = set(item.value for item in ts3enums.ConnectionProperties)
                if i in values: msg += " ({})".format(ts3enums.ConnectionProperties(i))
                msg += ": "
                (err, var) = ts3lib.getConnectionVariableAsString(schid, clid, i)
                if err != ts3defines.ERROR_ok:
                    (_err, var) = ts3lib.getErrorMessage(err)
                msg += var
                with open(self.filepath, "a", encoding="utf-8") as myfile:
                    myfile.write(msg+"\n")
                ts3lib.printMessageToCurrentTab(msg)
        else: return False
        return True

    def onConnectionInfoEvent(self, schid, clid):
        if clid != self.req: return
        self.req = 0
        ts3lib.printMessageToCurrentTab("onConnectionInfoEvent: %s"%clientURL(schid, clid))

    def onUpdateClientEvent(self, schid, clid, invokerID, invokerName, invokerUID):
        if clid != self.req: return
        self.req = 0
        ts3lib.printMessageToCurrentTab("onUpdateClientEvent: %s"%clientURL(schid, clid))