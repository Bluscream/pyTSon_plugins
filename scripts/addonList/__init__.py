# t = pluginhost.PluginHost.plugins["eventlog"]
import pytson, ts3lib, ts3defines, pluginhost, re
from ts3plugin import ts3plugin
from datetime import datetime
import xml.etree.ElementTree as xml

class addonList(ts3plugin):
    name = "Addon Scanner"
    apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "App Scanner like, just addons here"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = "[b]Addons[/b]:"
    menuItems = []
    hotkeys = []
    debug = True

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        self.setMeta(ts3lib.getCurrentServerConnectionHandlerID())
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def infoData(self, schid, id, atype): # https://github.com/teamspeak-plugins/now_playing/blob/master/now_playing/nowplaying_plugin.c#L667
        if atype == 2:
            i = []
            (error, meta) = ts3lib.getClientVariableAsString(schid, id, ts3defines.ClientProperties.CLIENT_META_DATA)
            try:
                meta = re.search('<addons>(.+?)</addons>', meta).group(0)
            except AttributeError: return
            addons = xml.fromstring(meta)
            try:
                scripts = addons.find("pytson").findall("script")
                i.append("[u]pyTSon[/u]:")
                for script in scripts:
                    try: i.append("{name} v{version} by {author}".format(name=script.text,version=script.attrib["version"],author=script.attrib["author"]))
                    except: continue
            except: pass
            return i
        #     for name, plugin in pluginhost.PluginHost.plugins.items():
        #         try: i.append("{name} v{version} by {author}".format(name=plugin.name,version=plugin.version,author=plugin.author))
        #         except:
        #             if self.debug: from traceback import format_exc;ts3lib.logMessage("Error listing {0}: {1}".format(plugin, format_exc()), ts3defines.LogLevel.LogLevel_ERROR, self.name, schid)
        #             continue
        #     return i

    def setMeta(self, schid, ownID=None):
        if ownID == None: (error, ownID) = ts3lib.getClientID(schid)
        (error, oldmeta) = ts3lib.getClientVariableAsString(schid, ownID, ts3defines.ClientProperties.CLIENT_META_DATA)
        # e = xml.etree.ElementTree.parse('<addons><pytson></pytson></addons>').getroot()
        if '<addons>' in oldmeta:
            oldmeta = re.sub(r"<addons>.*</addons>", "", oldmeta)
        newmeta = xml.Element('addons')
        pytson = xml.SubElement(newmeta, "pytson")
        for name, plugin in pluginhost.PluginHost.plugins.items():
            script = xml.SubElement(pytson, "script",{'version': plugin.version, 'author': plugin.author})
            script.text = plugin.name
        error = ts3lib.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_META_DATA, "{old}{new}".format(old=oldmeta,new=xml.tostring(newmeta).decode("utf-8")))
        if not error == ts3defines.ERROR_ok: ts3lib.printMessageToCurrentTab("Error: Unable to set own meta data to \"%s\"."%root);return False

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: self.setMeta(schid)
