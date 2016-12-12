from ts3plugin import ts3plugin
import ts3, ts3defines
import re
class autopoke(ts3plugin):
    name = "kickoldself"
    requestAutoload = True
    version = "1.0"
    apiVersion = 21
    author = "Thomas \"PLuS\" Pathmann"
    description = "Kick my zombie eg after a crash"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    def onConnectStatusChangeEvent(self, schid, status, errorNumber):
        if status != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        (err, mynick) = ts3.getClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if err != ts3defines.ERROR_ok: return
        sp = re.split(r"\d", mynick)
        if len(sp) > 1 and sp[0] != mynick and sp[1] == "":
            (err, clis) = ts3.getClientList(schid)
            if err == ts3defines.ERROR_ok:
                for cli in clis:
                    (err, nick) = ts3.getClientVariableAsString(schid, cli, ts3defines.ClientProperties.CLIENT_NICKNAME)
                    if err == ts3defines.ERROR_ok and nick == sp[0]:
                        ts3.requestClientKickFromServer(schid, cli, "Client not responding")
                        ts3.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_NICKNAME, sp[0])
                        ts3.flushClientSelfUpdates(schid)
                        return
