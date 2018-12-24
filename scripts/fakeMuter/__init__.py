import ts3lib as ts3
from ts3plugin import ts3plugin, PluginHost
import ts3defines
import pytson
import datetime, os, time


class fakeMuter(ts3plugin):
    name = "fakeMuter"
    apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = True
    version = "1.0"
    author = "Exp"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = ""
    menuItems = []
    hotkeys = [("fakeMute", "fakeMute")]
    debug = False
    enabled = False
    changeName = True

    def __init__(self):
        ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by "+self.author+" loaded.")

    def onHotkeyEvent(self, keyword):
        if keyword == "fakeMute":
            self.enabled = not self.enabled
            if self.changeName:
                name = ts3.getClientDisplayName(1,ts3.getClientID(1), 128)
                if enabled:
                    ts3.setClientSelfVariableAsString(1, ts3defines.CLIENT_NICKNAME, name + " [MUTED]")
                else:
                    ts3.setClientSelfVariableAsString(1, ts3defines.CLIENT_NICKNAME, name[:-8])
                ts3.flushClientSelfUpdates(1, "")

    def onEditPlaybackVoiceDataEvent(self, clientID, samples, sampleCount, channels):
        if self.enabled:
            samples = 0