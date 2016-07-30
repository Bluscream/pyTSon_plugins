from ts3plugin import ts3plugin, PluginHost
import ts3lib, ts3defines, datetime, ts3query


class queryConsole(ts3plugin):
    name = "TS3 Query Console"
    import pytson;apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Adds a query console to your Teamspeak 3 Client.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Show Query Console", "")]
    hotkeys = []
    debug = False
    toggle = True

    def __init__(self):
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug:
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            with ts3.query.TS3Connection("localhost") as ts3conn:
                # Note, that the client will wait for the response and raise a
                # **TS3QueryError** if the error id of the response is not 0.
                try:
                        ts3conn.login(
                                client_login_name="serveradmin",
                                client_login_password=""
                        )
                except ts3.query.TS3QueryError as err:
                        print("Login failed:", err.resp.error["msg"])
                        exit(1)

                ts3conn.use(sid=1)

                # Each query method will return a **TS3QueryResponse** instance,
                # with the response.
                resp = ts3conn.clientlist()
                print("Clients on the server:", resp.parsed)
                print("Error:", resp.error["id"], resp.error["msg"])

                # Note, the TS3Response class and therefore the TS3QueryResponse
                # class too, can work as a rudimentary container. So, these two
                # commands are equal:
                for client in resp.parsed:
                        print(client)
                for client in resp:
                        print(client)

    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        if self.toggle:
            if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHING:
                print("hi")
