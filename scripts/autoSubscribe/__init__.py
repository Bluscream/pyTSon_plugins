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
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Sub all non-pw channels", ""),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "Unsub from all channels", "")]
    hotkeys = []
    debug = True
    passwords = ["pw", "password", "passwort"]
    blacklist = [".fm", "radio", "music", "musik"]

    def __init__(self):
        ts3lib.logMessage(self.name + " script for pyTSon by " + self.author + " loaded from \"" + __file__ + "\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format( datetime.datetime.now()) + " [color=orange]" + self.name + "[/color] Plugin for pyTSon by [url=https://github.com/" + self.author + "]" + self.author + "[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0: self.subscribeAll(schid)
            elif menuItemID == 1: self.subscribeOpen(schid)
            elif menuItemID == 2: self.unsubscribeAll(schid)


    def subscribeAll(self, schid):
        try:
            error = ts3lib.requestChannelSubscribeAll(schid)
            if not error == ts3defines.ERROR_ok: raise Exception("Error in requestChannelSubscribeAll")
        except:
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

    def unsubscribeAll(self, schid):
        try:
            error = ts3lib.requestChannelUnsubscribeAll(schid)
            if not error == ts3defines.ERROR_ok: raise Exception("Error in requestChannelUnsubscribeAll")
        except:
            try:
                (error, clist) = ts3lib.getChannelList(schid)
                ts3lib.requestChannelUnsubscribe(schid, clist)
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
                (error, name) = ts3lib.getChannelVariableAsString(schid, c, ts3defines.ChannelProperties.CHANNEL_NAME)
                (error, pw) = ts3lib.getChannelVariableAsInt(schid, c, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
                (error, permanent) = ts3lib.getChannelVariableAsInt(schid, c, ts3defines.ChannelProperties.CHANNEL_FLAG_PERMANENT)
                (error, semiperm) = ts3lib.getChannelVariableAsInt(schid, c, ts3defines.ChannelProperties.CHANNEL_FLAG_SEMI_PERMANENT)
                (error, codec) = ts3lib.getChannelVariableAsInt(schid, c, ts3defines.ChannelProperties.CHANNEL_CODEC)
                if not pw and not permanent and not semiperm and not codec == ts3defines.CodecType.CODEC_OPUS_MUSIC and not any(x in name.lower() for x in self.blacklist): ts3lib.requestChannelSubscribe(schid, [c]) #clist.remove(c)
            # ts3lib.requestChannelSubscribe(schid, clist)
        except:
            try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0);pass
            except:
                try: from traceback import format_exc;ts3lib.printMessageToCurrentTab(format_exc())
                except:
                    try: from traceback import format_exc;print(format_exc())
                    except: print("Unknown Error")

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber): pass  # if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: self.subscribeAll(schid)

    def onNewChannelCreatedEvent(self, schid, channelID, channelParentID, invokerID, invokerName, invokerUniqueIdentiﬁer): self.subscribe(schid, channelID)

    def onUpdateChannelEditedEvent(self, schid, channelID, invokerID, invokerName, invokerUniqueIdentiﬁer): self.subscribe(self, schid, channelID)

    def subscribe(self, schid, channelID):
        (error, name) = ts3lib.getChannelVariableAsString(schid, channelID, ts3defines.ChannelProperties.CHANNEL_NAME)
        (error, pw) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
        (error, subscribed) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_ARE_SUBSCRIBED)
        (error, codec) = ts3lib.getChannelVariableAsInt(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC)
        if not pw or any(x in name.lower() for x in self.passwords) or not any(x in name.lower() for x in self.blacklist) or not codec == ts3defines.CodecType.CODEC_OPUS_MUSIC:
            if not subscribed: ts3lib.requestChannelSubscribe(schid, [channelID])
        elif (pw and not any(x in name.lower() for x in self.passwords)) or any(x in name.lower() for x in self.blacklist) or codec == ts3defines.CodecType.CODEC_OPUS_MUSIC:
            if subscribed: ts3lib.requestChannelUnsubscribe(schid, [channelID])
