import pytson, ts3lib, ts3defines
from ts3plugin import ts3plugin
from pytsonui import setupUi
from PythonQt.QtGui import *
from configparser import ConfigParser
from os import path
import os
from datetime import datetime
import time as moduleTime


def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())


class NoX(ts3plugin):
    name = "BanBypasser (NoX)"
    apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = False
    version = "1.0"
    author = "Bluscream, exp111"
    description = "Fights for you against admin abuse!"
    offersConfigure = True
    commandKeyword = "nox"
    infoTitle = None
    iconPath = path.join("scripts", "NoX", "icons")
    soundPath = path.join(pytson.getPluginPath(), "scripts", "NoX", "sound")
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Change Identity", path.join(iconPath, "16x16_identity_manager.png")),
                            (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Toggle Anti-Move", path.join(iconPath, "32x32_move_client_to_own_channel")), 
                            (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "Toggle Anti-Channel-Kick", path.join(iconPath, "32x32_kick_from_channel.png")),
                            (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 3, "Toggle Anti-Server-Kick", path.join(iconPath, "32x32_kick_from_server.png")),
                            (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 4, "Toggle Anti-Server-Ban", path.join(iconPath, "32x32_ban_client.png")),  
                            (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 5, "Backup Now", path.join(iconPath, "16x16_urlcatcher.png"))]
    hotkeys = [("toggleMove", "Toggle the Anti-Move Feature")]
    ini = path.join(pytson.getPluginPath(), "scripts", "NoX", "settings.ini")
    cfg = ConfigParser()
    antiMoveStatus = True
    antiChannelKickStatus = True
    antiServerKickStatus = True
    antiServerBanStatus = True
    rejoinChannel = False
    oldChannelID = 0
    passwordList = ["123", "1234"]
    maxSleepTime = 300
    currentChannelPW = ""
    currentServerPW = ""
    permissions = [
        ("i_permission_modify_power", 75, True),
        ("i_client_permission_modify_power", 75, True),
        ("i_group_modify_power", 75, True),
        ("i_group_member_add_power", 75, True),
        ("b_virtualserver_token_add", True, True),
        ("b_virtualserver_token_list", True, True),
        ("b_virtualserver_token_use", True, True),
        ("b_virtualserver_token_delete", True, True),
        ("b_client_ignore_bans", True, True),
        ("b_client_remoteaddress_view", True, True)
    ]

    def backup(self, serverConnectionHandlerID):
        ownID = ts3lib.getClientID(serverConnectionHandlerID)[1]
        ip = ts3lib.getConnectionVariableAsString(serverConnectionHandlerID, ownID, ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)[1]
        self.cfg['data']['ip'] = ip
        port = ts3lib.getConnectionVariableAsUInt64(serverConnectionHandlerID, ownID, ts3defines.ConnectionProperties.CONNECTION_SERVER_PORT)[1]
        self.cfg['data']['port'] = str(port)
        serverPassword = ts3lib.getServerConnectInfo(serverConnectionHandlerID, 256)[3]
        self.currentServerPW = serverPassword
        nickname = ts3lib.getClientSelfVariableAsString(serverConnectionHandlerID, ts3defines.ClientProperties.CLIENT_NICKNAME)[1]
        self.cfg.set('data', 'nickname', nickname)
        tabID = ts3defines.PluginConnectTab.PLUGIN_CONNECT_TAB_CURRENT
        self.cfg['data']['tabID'] = str(tabID)
        channelID = ts3lib.getChannelOfClient(serverConnectionHandlerID, ownID)[1]
        channelPassword = ts3lib.getChannelConnectInfo(serverConnectionHandlerID, channelID, 256)[2]
        self.currentChannelPW = channelPassword
        return

    def sleep(self, time):
        #command = "ping 127.0.0.1 -n "+ str(time + 1) + " > nul"
        #os.system(command)

        #ntime = moduleTime.time() + time
        #while moduleTime.time() < ntime:
        #    pass
        moduleTime.sleep(time)
        return
        
    def TryJoinChannel(self, serverConnectionHandlerID, clientID, wantedChannelID):
        #verifyChannelPassword(serverConnectionHandlerID, channelID, channelPassword, returnCode)
        channelHasPassword = ts3lib.getChannelVariableAsInt(serverConnectionHandlerID, wantedChannelID, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)[1]
        if channelHasPassword == 1:
            ts3lib.requestClientMove(serverConnectionHandlerID, clientID, wantedChannelID, self.currentChannelPW)
        else:
            ts3lib.requestClientMove(serverConnectionHandlerID, clientID, wantedChannelID, "")
        self.backup(serverConnectionHandlerID)
        return

    def __init__(self):
        if path.isfile(self.ini):
            self.cfg.read(self.ini)
        else:
            self.cfg['general'] = { "cfgversion": "1", "debug": "False", "enabled": "True", "channelpw": "123", "serverpw": "123", "anticrash": "True" , "identity": "default"}
            self.cfg['antimove'] = { "enabled": "True", "delay": "0", "defaultstatus": "True", "message": "False"}
            self.cfg['antichannelkick'] = { "enabled": "True", "delay": "0", "defaultstatus": "True"}
            self.cfg['antichannelban'] = { "enabled": "True", "delay": "0"}
            self.cfg['antiserverkick'] = { "enabled": "True", "delay": "0", "defaultstatus": "True", "rejoinchannel": "True"}
            self.cfg['antiserverban'] = { "enabled": "True", "delay": "0", "defaultstatus": "True", "rejoinchannel": "True", "maxsleeptime": "300"}
            self.cfg['antichanneldelete'] = { "enabled": "True", "delay": "0"}
            self.cfg['data'] = { "ip": "127.0.0.1", "port": "9987", "channelid": "0", "channelname": "Default Channel", "nickname": "TeamspeakUser", "phoneticnick": "", "metaData": "", "tabID": "0", "identityPrefix": "Neue Identität_", "currentID": "1"}
            self.cfg['passwords'] = { "passwords": "123,1234"}
            with open(self.ini, 'w') as configfile:
                self.cfg.write(configfile)
        ts3lib.logMessage(self.name + " script for pyTSon by " + self.author + " loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        self.antiMoveStatus = self.cfg['antimove']['defaultstatus']
        self.antiChannelKickStatus = self.cfg['antichannelkick']['defaultstatus']
        self.antiServerKickStatus = self.cfg['antiserverkick']['defaultstatus']
        self.antiServerBanStatus = self.cfg['antiserverban']['defaultstatus']
        self.rejoinChannel = self.cfg['antiserverban']['rejoinchannel']
        self.passwordList = self.cfg['passwords']['passwords'].split(',')
        self.maxSleepTime = int(self.cfg['antiserverban']['maxsleeptime'])
        #ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now()) + " [color=orange]" + self.name + "[/color] Plugin for pyTSon by [url=https://github.com/" + self.author + "]" + self.author + "[/url] loaded.")
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        if schid != 0: self.backup(schid)
        ts3lib.printMessageToCurrentTab("[{:%Y-%m-%d %H:%M:%S}]".format(datetime.now()) + " Connected to [color=red]" + self.cfg['data']['ip'] + ":" + self.cfg['data']['port'] + "[/color] as [color=blue]" + self.cfg['data']['nickname'] + "[/color] on [color=green]Tab " + self.cfg['data']['tabID'] + "[/color]")

    def onMenuItemEvent(self, serverConnectionHandlerID, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0: 
                #self.reconnect(serverConnectionHandlerID)
                ownID = ts3lib.getClientID(serverConnectionHandlerID)[1]
                channelID = ts3lib.getChannelOfClient(serverConnectionHandlerID, ownID)[1]
                channelPassword = ts3lib.getChannelConnectInfo(serverConnectionHandlerID, channelID, 256)[2]
                ts3lib.printMessageToCurrentTab(channelPassword)
                ts3lib.playWaveFile(serverConnectionHandlerID, path.join(self.soundPath, "yee.wav"))
                ts3lib.printMessageToCurrentTab("Fuck off. You know this has no use. Like your life. Pew Pew.")
            if menuItemID == 1:
                self.antiMoveStatus = not self.antiMoveStatus
                ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=green]{2}[/color]".format(timestamp(), self.name, self.antiMoveStatus))
            if menuItemID == 2:
                self.antiChannelKickStatus = not self.antiChannelKickStatus
                ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=green]{2}[/color]".format(timestamp(), self.name, self.antiChannelKickStatus))
            if menuItemID == 3:
                self.antiServerKickStatus = not self.antiServerKickStatus
                ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=green]{2}[/color]".format(timestamp(), self.name, self.antiServerKickStatus))
            if menuItemID == 4:
                self.antiServerBanStatus = not self.antiServerBanStatus
                ts3lib.printMessageToCurrentTab("{0}Set {1} to [color=green]{2}[/color]".format(timestamp(), self.name, self.antiServerBanStatus))
            if menuItemID == 5:
                self.backup(serverConnectionHandlerID)
                ts3lib.printMessageToCurrentTab("{0}[color=green]Backup complete![/color]".format(timestamp()))

    def onHotkeyEvent(self, keyword):
        if keyword == "toggleMove":
            self.antiMoveStatus = not self.antiMoveStatus
            schid = ts3lib.getCurrentServerConnectionHandlerID()
            if self.antiMoveStatus:
                ts3lib.playWaveFile(schid, path.join(self.soundPath, "on.wav"))
            else:
                ts3lib.playWaveFile(schid, path.join(self.soundPath, "off.wav"))
            ts3lib.printMessageToCurrentTab("{0}{1}: Set Anti-Move to [color=green]{2}[/color]".format(timestamp(), self.name, self.antiMoveStatus))
        return

    def processCommand(self, serverConnectionHandlerID, command):
        if command == "toggleMove":
            self.antiMoveStatus = not self.antiMoveStatus
            if self.antiMoveStatus:
                ts3lib.playWaveFile(serverConnectionHandlerID, path.join(self.soundPath, "on.wav"))
            else:
                ts3lib.playWaveFile(serverConnectionHandlerID, path.join(self.soundPath, "off.wav"))
            ts3lib.printMessageToCurrentTab("{0}{1}: Set Anti-Move to [color=green]{2}[/color]".format(timestamp(), self.name, self.antiMoveStatus))
            return True
        else:
            return False
        return False

    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        try:
            if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTED: #The server has accepted us, we can talk and hear and we got a clientID, but we don't have the channels and clients yet, we can get server infos (welcome msg etc.)
                pass
            elif newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: #we are CONNECTED and we have the client and channels available
                if self.cfg['antiserverkick']['rejoinchannel'] != "False" and self.rejoinChannel == True or self.cfg['antiserverban']['rejoinchannel'] != "False" and self.rejoinChannel == True:
                    clientID = ts3lib.getClientID(serverConnectionHandlerID)[1]
                    currentChannelID = ts3lib.getChannelOfClient(serverConnectionHandlerID, clientID)[1]
                    if currentChannelID != self.oldChannelID and self.oldChannelID != 0:
                        self.TryJoinChannel(serverConnectionHandlerID, clientID, self.oldChannelID)
                    self.rejoinChannel = False
                self.backup(serverConnectionHandlerID)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def currentServerConnectionChanged(self, serverConnectionHandlerID):
        clientID = ts3lib.getClientID(serverConnectionHandlerID)[1]
        ts3lib.printMessageToCurrentTab("{0}Server changed to {1}. The ClientID is now {2}".format(timestamp(), clientID))

    def onClientMoveEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        mClientID = ts3lib.getClientID(serverConnectionHandlerID)[1]
        if clientID == mClientID:
            if moveMessage == "":
                self.backup(serverConnectionHandlerID)
        return

    def onClientMoveMovedEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
        try:
            if self.cfg['antimove']['enabled'] != 'False' and self.antiMoveStatus != False:
                if serverConnectionHandlerID != 0:
                    mClientID = ts3lib.getClientID(serverConnectionHandlerID)
                    if mClientID[1] == clientID:
                        self.TryJoinChannel(serverConnectionHandlerID, clientID, oldChannelID)
                        self.backup(serverConnectionHandlerID)
                        ts3lib.playWaveFile(serverConnectionHandlerID, path.join(self.soundPath, "noice.wav"))
                        if self.cfg['antimove']['message'] == 'True': 
                            message = 'Stop it ' + moverName + '!'
                            ts3lib.requestSendPrivateTextMsg(serverConnectionHandlerID, message, moverID) 
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onClientKickFromChannelEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        try:
            if self.cfg['antichannelkick']['enabled'] != 'False' and self.antiChannelKickStatus != False:
                if serverConnectionHandlerID != 0:
                    mClientID = ts3lib.getClientID(serverConnectionHandlerID)
                    if mClientID[1] == clientID:
                        self.TryJoinChannel(serverConnectionHandlerID, clientID, oldChannelID)
                    self.backup(serverConnectionHandlerID)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onClientKickFromServerEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        try:
            if self.cfg['antiserverkick']['enabled'] != 'False' and self.antiServerKickStatus != False:
                tabID = int(self.cfg['data']['tabID'])
                ip = self.cfg['data']['ip']
                port = self.cfg['data']['port']
                #serverPw = self.cfg['general']['serverpw']
                serverPw = self.currentServerPW
                nickname = self.cfg['data']['nickname']
                channelList = []
                channelPw = self.cfg['general']['channelpw']
                identity = self.cfg['general']['identity']
                address = ip + ":" + port
                (error, schid) = ts3lib.guiConnect(tabID, "Server", address, serverPw, nickname, "", channelPw, "default", "default", "default", "default", identity, "", "")
                if self.cfg['antiserverkick']['rejoinchannel'] != "False":
                    self.oldChannelID = oldChannelID
                    self.rejoinChannel = True
                self.backup(schid)
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def onClientBanFromServerEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, time, kickMessage):
        try:
            ts3lib.playWaveFile(serverConnectionHandlerID, path.join(self.soundPath, "ahfuck.wav"))
            ts3lib.printMessageToCurrentTab("fuck")
            if self.cfg['antiserverban']['enabled'] != 'False' and self.antiServerBanStatus != False:
                if time != 0 and time < self.maxSleepTime:
                    tabID = int(self.cfg['data']['tabID'])
                    ip = self.cfg['data']['ip']
                    port = self.cfg['data']['port']
                    #serverPw = self.cfg['general']['serverpw']
                    serverPw = self.currentServerPW
                    nickname = self.cfg['data']['nickname']
                    channelList = []
                    channelPw = self.cfg['general']['channelpw']
                    identity = self.cfg['general']['identity']
                    address = ip + ":" + port
                    if time > 30:
                        time = time + 1
                    self.sleep(time)
                    (error, schid) = ts3lib.guiConnect(tabID, "Server", address, serverPw, nickname, "", channelPw, "default", "default", "default", "default", identity, "", "")
                    if self.cfg['antiserverban']['rejoinchannel'] != "False":
                        self.rejoinChannel = True
                        self.oldChannelID = oldChannelID
                self.backup(schid)
                #identity = self.cfg['data']['identityPrefix'] + self.cfg['data']['currentID']
                #(error, schid) = ts3lib.guiConnect(tabID, "Server", address, serverPw, nickname, "", channelPw, "", "", "", "default", identity, "", "")
                #self.cfg['data']['currentID'] = self.cfg['data']['currentID'] + 1
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
    
    def onServerGroupClientAddedEvent(self, schid, clientID, clientName, clientUniqueIdentity, serverGroupID, invokerClientID, invokerName, invokerUniqueIdentity):
        try:
            mClientID = ts3lib.getClientID(schid)[1]
            if mClientID == clientID:
                clientDatabaseID = ts3lib.getClientVariableAsString(schid, mClientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)[1]
                pids = [];pvals = [];pskips = []
                for perm in self.permissions:
                    pids.append(ts3lib.getPermissionIDByName(schid, perm[0])[1])
                    pvals.append(perm[1])
                    pskips.append(perm[2])
                result = ts3lib.requestClientAddPerm(schid, int(clientDatabaseID), pids, pvals, pskips)
                if result == True:
                    ts3lib.printMessageToCurrentTab("[{:%Y-%m-%d %H:%M:%S}]".format(datetime.now()) + "[color=green] Completed exploiting dumb people[/color]")
                else:
                    ts3lib.printMessageToCurrentTab("[{:%Y-%m-%d %H:%M:%S}]".format(datetime.now()) + "[color=red] Failed giving permissions[/color]")
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)