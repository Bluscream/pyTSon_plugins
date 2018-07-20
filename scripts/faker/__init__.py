#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ts3lib, ts3defines, sys
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from ts3Ext import ts3SessionHost, logLevel
from bluscream import timestamp

class faker(ts3plugin):
    name = "Fake Anything"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Fake almost anything ;)"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Fake this channel", "scripts/%s/fake.png"%__name__),
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Fake this client", "scripts/%s/fake.png"%__name__)]
    hotkeys = []
    ts3host = None
    guiLogLvl = logLevel.ALL

    def __init__(self):
        if "aaa_ts3Ext" in PluginHost.active: self.ts3host = PluginHost.active["aaa_ts3Ext"].ts3host
        else: self.ts3host = ts3SessionHost(self)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL and menuItemID == 0: self.fakeChannel(schid, selectedItemID)
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT and menuItemID == 0: self.fakeClient(schid, selectedItemID)

    def fakeChannel(self, schid, channelID):
        channel = self.ts3host.getChannel(schid, channelID)
        debug = PluginHost.cfg.getboolean("general", "verbose")
        (error, name) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_NAME)
        # name = name.encode("utf-8").decode(sys.stdout.encoding)
        # TODO MODIFY NAME
        if debug: print("err:", error, "CHANNEL_NAME", name)
        if not error and name: ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_NAME,name)

        (error, phonetic) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC)
        if debug: print("err:", error, "CHANNEL_NAME_PHONETIC", phonetic)
        if not error and phonetic: ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC,phonetic)

        (error, pw) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
        if debug: print("err:", error, "CHANNEL_FLAG_PASSWORD", pw)
        if pw:
            (err, path, _pw) = ts3lib.getChannelConnectInfo(schid, channelID)
            if debug: print("err:", error, "_pw", _pw)
            ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_PASSWORD,_pw if _pw else ".")
        """
        (error, topic) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_TOPIC)
        if debug: print("err:", error, "CHANNEL_TOPIC", topic)
        if not error and topic: ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_TOPIC,topic)

        ts3lib.requestChannelDescription(schid, channelID)
        (error, description) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_DESCRIPTION)
        if debug: print("err:", error, "CHANNEL_DESCRIPTION", description)
        if not error and description: ts3lib.setChannelVariableAsString(schid, 0,ts3defines.ChannelProperties.CHANNEL_DESCRIPTION,description.decode('utf-8'))
        """
        (error, neededtp) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
        if debug: print("err:", error, "CHANNEL_NEEDED_TALK_POWER", neededtp)
        if not error and neededtp: ts3lib.setChannelVariableAsInt(schid, 0,ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER,neededtp)

        (error, codec) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC)
        if debug: print("err:", error, "CHANNEL_CODEC", codec)
        if not error and codec: ts3lib.setChannelVariableAsInt(schid, 0,ts3defines.ChannelProperties.CHANNEL_CODEC,codec)

        (error, quality) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC_QUALITY)
        if debug: print("err:", error, "CHANNEL_CODEC_QUALITY", quality)
        if not error and quality: ts3lib.setChannelVariableAsInt(schid, 0,ts3defines.ChannelProperties.CHANNEL_CODEC_QUALITY,quality)

        (error, latency) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC_LATENCY_FACTOR)
        if debug: print("err:", error, "CHANNEL_CODEC_LATENCY_FACTOR", latency)
        if not error and latency: ts3lib.setChannelVariableAsInt(schid, 0,ts3defines.ChannelProperties.CHANNEL_CODEC_LATENCY_FACTOR,latency)

        (error, unencrypted) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_CODEC_IS_UNENCRYPTED)
        if debug: print("err:", error, "CHANNEL_CODEC_IS_UNENCRYPTED", unencrypted)
        if not error and unencrypted: ts3lib.setChannelVariableAsInt(schid, 0,ts3defines.ChannelProperties.CHANNEL_CODEC_IS_UNENCRYPTED,unencrypted)

        (error, maxclients) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS)
        if debug: print("err:", error, "CHANNEL_MAXCLIENTS", maxclients)
        if not error and maxclients: ts3lib.setChannelVariableAsInt(schid, 0,ts3defines.ChannelProperties.CHANNEL_MAXCLIENTS,maxclients)

        (error, maxfamilyclients) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelProperties.CHANNEL_MAXFAMILYCLIENTS)
        if debug: print("err:", error, "CHANNEL_MAXFAMILYCLIENTS", maxfamilyclients)
        if not error and maxfamilyclients: ts3lib.setChannelVariableAsInt(schid, 0,ts3defines.ChannelProperties.CHANNEL_MAXFAMILYCLIENTS,maxfamilyclients)

        (error, iconid) = ts3lib.getChannelVariable(schid, channelID, ts3defines.ChannelPropertiesRare.CHANNEL_ICON_ID)
        if debug: print("err:", error, "CHANNEL_ICON_ID", iconid)
        if not error and iconid: ts3lib.setChannelVariableAsInt(schid, 0,ts3defines.ChannelPropertiesRare.CHANNEL_ICON_ID,iconid)

        ts3lib.flushChannelCreation(schid, 0)

    def fakeClient(self, schid, clientID):
        (error, _clid) = ts3lib.getClientID(schid)
        (error, tnick) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientProperties.CLIENT_NICKNAME)
        (error, tnickp) = ts3lib.getClientVariable(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_NICKNAME_PHONETIC)
        ts3lib.flushClientSelfUpdates(schid)