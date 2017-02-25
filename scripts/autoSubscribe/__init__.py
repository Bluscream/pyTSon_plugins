import ts3lib, ts3defines, datetime
from ts3plugin import ts3plugin, PluginHost
from os import path


class autoSubscribe(ts3plugin):
    name = "Auto Subscribe"
    apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Manage your channel subscriptions the way YOU want."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    iconPath = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "autoSubscribe", "icons")
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Subscribe to all channels", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Sub all non-pw channels", "")]
    hotkeys = []
    debug = False

    def __init__(self):
        ts3lib.logMessage(self.name + " script for pyTSon by " + self.author + " loaded from \"" + __file__ + "\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format( datetime.now()) + " [color=orange]" + self.name + "[/color] Plugin for pyTSon by [url=https://github.com/" + self.author + "]" + self.author + "[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0:
                self.subscribeAll(schid)
            elif menuItemID == 1:
                self.subscribeOpen(schid)

    def subscribeAll(self, schid):
        try:
            (error, clist) = ts3lib.getChannelList(schid)
            ts3lib.requestChannelSubscribe(schid, clist)
        except:
            try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0);pass
            except:
                try: from traceback import format_exc;ts3lib.printMessageToCurrentTab(format_exc())
                except:
                    try: from traceback import format_exc;print(format_exc())
                    except: print("Unknown Error")


    def subscribeOpen(self, schid):
        try:
            (error, clist) = ts3lib.getChannelList(schid)
            for c in clist:
                (error, pw) = ts3lib.getChannelVariableAsInt(schid, c, ts3defines.ChannelProperties.CHANNEL_PASSWORD)
                if not pw: clist.remove(c)
            ts3lib.requestChannelSubscribe(schid, clist)
        except:
            try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0);pass
            except:
                try: from traceback import format_exc;ts3lib.printMessageToCurrentTab(format_exc())
                except:
                    try: from traceback import format_exc;print(format_exc())
                    except: print("Unknown Error")

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        pass  # if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: self.subscribeAll(schid)

    def onNewChannelCreatedEvent(self, schid, channelID, channelParentID, invokerID, invokerName, invokerUniqueIdentiﬁer):
        (error, name) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_NAME)
        (error, pw) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_PASSWORD)
        if not pw or "pw" in name.lower() or "passwort" in name.lower() or "password" in name.lower(): ts3lib.requestChannelSubscribe(schid, [channelID])

    def onUpdateChannelEditedEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentiﬁer) :
        (error, name) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_NAME)
        (error, pw) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_PASSWORD)
        if not pw or "pw" in name.lower() or "passwort" in name.lower() or "password" in name.lower(): ts3lib.requestChannelSubscribe( schid, [channelID])
