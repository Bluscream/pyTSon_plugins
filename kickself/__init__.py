from ts3plugin import ts3plugin
import ts3lib, ts3defines, re
class autopoke(ts3plugin):
    name = "kickoldself"
    requestAutoload = False
    version = "1.0"

    apiVersion = 22
    author = "Thomas \"PLuS\" Pathmann"
    description = "Kick my zombie eg after a crash"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    def onConnectStatusChangeEvent(self, schid, status, errorNumber):
        if status != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        (err, mynick) = ts3lib.getClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if err != ts3defines.ERROR_ok: return
        sp = re.split(r"\d", mynick)
        if len(sp) > 1 and sp[0] != mynick and sp[1] == "":
            (err, clis) = ts3lib.getClientList(schid)
            if err == ts3defines.ERROR_ok:
                for cli in clis:
                    (err, nick) = ts3lib.getClientVariableAsString(schid, cli, ts3defines.ClientProperties.CLIENT_NICKNAME)
                    if err == ts3defines.ERROR_ok and nick == sp[0]:
                        ts3lib.requestClientKickFromServer(schid, cli, "Client not responding")
                        ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, sp[0])
                        ts3lib.flushClientSelfUpdates(schid)
                        return
