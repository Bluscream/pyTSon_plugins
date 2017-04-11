from ts3plugin import ts3plugin
from datetime import datetime
from urllib.parse import quote as urlencode
import ts3defines, ts3lib

class showQueries(ts3plugin):
    name = "Query Viewer"
    import pytson;apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Shows you queries in channels.\n\nHomepage: https://github.com/Bluscream/Extended-Info-Plugin\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = "[b]Queries:[/b]"
    menuItems = []
    hotkeys = []
    debug = False

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def clientURL(self, schid=None, clid=1, uid=None, nickname=None, encodednick=None):
        if schid == None:
            try: schid = ts3lib.getCurrentServerConnectionHandlerID()
            except: pass
        if uid == None:
            try: (error, uid) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            except: pass
        if nickname == None:
            try: (error, nickname) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
            except: nickname = uid
        if encodednick == None:
            try: encodednick = urlencode(nickname)
            except: pass
        return "[url=client://{0}/{1}~{2}]{3}[/url]".format(clid, uid, encodednick, nickname)

    def infoData(self, schid, id, atype):
        try:
            if atype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
                (error, clist) = ts3lib.getChannelClientList(schid, id)
                i = []
                for c in clist:
                    (error, clienttype) = ts3lib.getClientVariableAsInt(schid, c, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
                    if clienttype == ts3defines.ClientType.ClientType_SERVERQUERY:
                        i.append(self.clientURL(schid,c))
                if len(i) < 1: return
                else: return i
        except: return
