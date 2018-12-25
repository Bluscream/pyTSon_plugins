from ts3plugin import ts3plugin
import ts3lib, ts3defines, re
from PythonQt.QtCore import QTimer

class autopoke(ts3plugin):
    name = "kickoldself"
    requestAutoload = False
    version = "1.0"
    apiVersion = 22
    author = "Thomas \"PLuS\" Pathmann, Edited by Bluscream"
    description = "Kick my zombie eg after a crash"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    schid = 0; newnick = ""

    def onConnectStatusChangeEvent(self, schid, status, errorNumber):
        if status != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        (err, mynick) = ts3lib.getClientSelfVariable(schid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        if err != ts3defines.ERROR_ok: return
        sp = re.split(r"\d", mynick)
        if len(sp) > 1 and sp[0] != mynick and sp[1] == "":
            (err, clis) = ts3lib.getClientList(schid)
            if err != ts3defines.ERROR_ok: return
            for cli in clis:
                (err, nick) = ts3lib.getClientVariable(schid, cli, ts3defines.ClientProperties.CLIENT_NICKNAME)
                if err == ts3defines.ERROR_ok and nick == sp[0]:
                    err = ts3lib.requestClientKickFromServer(schid, cli, "Client not responding")
                    self.schid = schid; self.newnick = sp[0]
                    ts3lib.printMessageToCurrentTab('err: {0}'.format(err))
                    if err == ts3defines.ERROR_ok: self.rename()
                    else: QTimer.singleShot(30000, self.rename)

    def rename(self):
        ts3lib.setClientSelfVariableAsString(self.schid, ts3defines.ClientProperties.CLIENT_NICKNAME, self.newnick)
        self.schid = 0; self.newnick = ""
        ts3lib.flushClientSelfUpdates(self.schid)