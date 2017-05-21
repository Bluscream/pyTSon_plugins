import ts3defines, ts3lib, json, string, random
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PythonQt.QtCore import QUrl
from urllib.parse import quote_plus as urlencode
from ts3plugin import ts3plugin
from datetime import datetime
from os import path
from configparser import ConfigParser

class autoChannelCreate(ts3plugin):
    name = "Auto Channel Creator"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Automatically create your favorite channels.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Auto Talk Power", "")]
    hotkeys = []
    debug = False
    ini = path.join(pytson.getPluginPath(), "scripts", __name__, "settings.ini")
    cfg = ConfigParser()

    def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def randomstring(size=40,chars=string.ascii_letters+string.digits): return ''.join(random.choice(chars) for _ in range(size))

    def __init__(self):
        if path.isfile(self.ini): self.cfg.read(self.ini)
        else:
            self.cfg['general'] = {"cfgversion": "1", "debug": "False", "enabled": "True"}
            with open(self.ini, 'w') as configfile: self.cfg.write(configfile)
        ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def configure(self, qParentWidget): pass

    def createChannel(self,
    name=randomstring(),
    phonetic="",
    password="",
    topic="",
    description="",
    type=None,
    default=False,
    order="",
    neededtp="",
    codec=ts3defines.CodecType.CODEC_OPUS_VOICE,
    codecquality=5, # 0-10
    codeclatency=1, # 1-10
    deletedelay=0,
    encrypted=False,
    maxclients=-1,
    maxfamilyclients=-1):
        pass

    def editChannel(self,
    name=randomstring(),
    phonetic=None,
    password=None,
    topic=None,
    description=None,
    type=None,
    default=None,
    order=None,
    neededtp=None,
    codec=None,
    codecquality=None, # 0-10
    codeclatency=None, # 1-10
    deletedelay=None,
    encrypted=None,
    maxclients=None,
    maxfamilyclients=None):
        pass

    def setChannelVariables(self): pass
