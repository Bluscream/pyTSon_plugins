try:
    import ts3lib
    from urllib.parse import quote as urlencode
    from ts3plugin import ts3plugin, PluginHost
    # noinspection PyUnresolvedReferences
    from PythonQt.QtSql import QSqlDatabase
    import ts3defines, re
    from configparser import ConfigParser
    from os import path
    from datetime import datetime

    class channelWatcher(ts3plugin):
        name = "Channel Watcher"
        import pytson;apiVersion = pytson.getCurrentApiVersion()
        requestAutoload = False
        version = "1.0"
        author = "Bluscream"
        description = "Helps you keeping your channel moderated.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
        offersConfigure = False
        commandKeyword = "cw"
        infoTitle = None
        menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle Channel Watcher", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Add to watched channels", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 1, "Remove from watched channels", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Check this client!", "")]
        hotkeys = []
        debug = True
        toggle = True
        autoBan = True
        autoMod = True
        autoBanOnKick = True
        checkRecording = True
        autoCheckOnChannel = False
        requested = False
        #requestedUID = []
        requestedC = []
        banned = False
        banned_names = ["BAN", "NOT WELCOME"]
        mod_names = ["MOD", "OPERATOR"]
        admin_names = ["ADMIN"]
        sbgroup = 0
        smgroup = 0
        sagroup = 0
        ownchannels = []
        check = False
        checkcurrent = ""
        reason = ""
        ini = path.join(pytson.getPluginPath(), "scripts", "channelWatcher", "settings.ini")
        cfg = ConfigParser()

        def timestamp(self): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

        def __init__(self):
            if path.isfile(self.ini): self.cfg.read(self.ini)
            else:
                self.cfg['general'] = {"cfgversion": "1", "debug": "False", "enabled": "True"}
                self.cfg['autoban'] = {"enabled": "True"}
                self.cfg['automod'] = {"enabled": "True", "autotp": "True"}
                self.cfg['antirecord'] = {"enabled": "True"}
                self.cfg['autokickonban'] = {"enabled": "True"}
                self.cfg['groups'] = {"banned": ["BAN", "NOT WELCOME"], "mod": ["MOD", "OPERATOR"], "admin": ["ADMIN"]}
                with open(self.ini, 'w') as configfile: self.cfg.write(configfile)
            self.db = QSqlDatabase.addDatabase("QSQLITE","channelWatcher")
            self.db.setDatabaseName(ts3lib.getConfigPath() + "settings.db")
            if self.db.isValid(): self.db.open()
            schid = ts3lib.getCurrentServerConnectionHandlerID()
            if schid:
                self.requested = True
                ts3lib.requestChannelGroupList(schid)
                (error, ownID) = ts3lib.getClientID(schid)
                (error, cid) = ts3lib.getChannelOfClient(schid, ownID)
                self.ownchannels.extend([cid])
            ts3lib.logMessage("{0} script for pyTSon by {1} loaded from \"{2}\".".format(self.name,self.author,__file__), ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
            if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

        def stop(self):
            self.db.close();self.db.delete()
            QSqlDatabase.removeDatabase("channelWatcher")

        def clientURL(self, schid=None, clid=1, uid=None, nickname=None, encodednick=None):
            if not self.check: return False
            if schid == None:
                try: schid = ts3lib.getCurrentServerConnectionHandlerID()
                except: pass
            if uid == None:
                try: (error, uid) = ts3lib.getClientVariableAsString(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                except: pass
            if nickname == None:
                try: (error, nickname) = ts3lib.getClientDisplayName(schid, clid)
                except: nickname = uid
            if encodednick == None:
                try: encodednick = urlencode(nickname)
                except: pass
            return "[url=client://%s/%s~%s]%s[/url]" % (clid, uid, encodednick, nickname)

        def InContacts(self, uid):
            if not self.check: return False
            q = self.db.exec_("SELECT * FROM contacts WHERE value LIKE '%%IDS=%s%%'" % uid)
            ret = 2
            if q.next():
                val = q.value("value")
                for l in val.split('\n'):
                    if l.startswith('Friend='):
                        ret = int(l[-1])
            q.delete();return ret

        def checkUser(self, uid):
            if not self.check: return False
            if self.toggle:
                if len(self.ownchannels) > 0:
                    if uid != "serveradmin" and uid != "ServerQuery":
                        _in = self.InContacts(uid)
                        if _in < 2:
                            _schid = ts3lib.getCurrentServerConnectionHandlerID()
                            self.requestedC.extend([_in])
                            ts3lib.requestClientDBIDfromUID(_schid, uid)

        def checkAllUsers(self):
            if not self.check: return False
            if self.toggle:
                _schid = ts3lib.getCurrentServerConnectionHandlerID()
                (error, _clid) = ts3lib.getClientID(_schid)
                (error, cl) = ts3lib.getClientList(_schid)
                for user in cl:
                    if user != _clid:
                        (error, uid) = ts3lib.getClientVariableAsString(_schid, user, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                        self.checkUser(uid)

        def processCommand(self, schid, command):
            cmd = command.lower()
            if cmd.startswith("test"):
                ts3lib.printMessageToCurrentTab("Status: "+str(self.toggle))
                ts3lib.printMessageToCurrentTab("Ban: "+str(self.sbgroup))
                ts3lib.printMessageToCurrentTab("Mod: "+str(self.smgroup))
                ts3lib.printMessageToCurrentTab("Admin: "+str(self.sagroup))
                ts3lib.printMessageToCurrentTab("Own Channels: "+str(self.ownchannels))
                ts3lib.printMessageToCurrentTab("requestedCs: "+str(self.requestedC))
                return True
            elif cmd.startswith("addchan"):
                command = int(command.split("addchan ")[1])
                self.ownchannels.extend([command])
                ts3lib.printMessageToCurrentTab("[color=green]Added[/color] #"+str(command)+" to list of channels: "+str(self.ownchannels))
                return True
            elif cmd.startswith("delchan"):
                command = int(command.split("delchan ")[1])
                self.ownchannels.remove([command])
                ts3lib.printMessageToCurrentTab("[color=red]Removed[/color] #"+str(command)+" from list of channels: "+str(self.ownchannels))
                return True
            elif cmd == "checkall":
                self.checkAllUsers()
                return True
            elif cmd == "load":
                self.requested = True
                ts3lib.requestChannelGroupList(ts3lib.getCurrentServerConnectionHandlerID())
                return True

        def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
            if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
                if menuItemID == 0:
                    self.toggle = not self.toggle
                    ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.datetime.now())+" Set Auto Channel Commander to [color=yellow]"+str(self.toggle)+"[/color]")
            elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL:
                if menuItemID == 0:
                    self.ownchannels.extend([selectedItemID])
                    ts3lib.printMessageToCurrentTab("[color=green]Added[/color] #"+str(selectedItemID)+" to list of channels: "+str(self.ownchannels))
                elif menuItemID == 1:
                    self.ownchannels.remove(selectedItemID)
                    ts3lib.printMessageToCurrentTab("[color=red]Removed[/color] #"+str(selectedItemID)+" from list of channels: "+str(self.ownchannels))
            elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
                if menuItemID == 0:
                    (error, uid) = ts3lib.getClientVariableAsString(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER);self.checkUser(uid)

        def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
            if self.toggle:
                if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
                    self.requested = True
                    ts3lib.requestChannelGroupList(schid)
                elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
                    self.check = False;self.ownchannels.clear()

        def onChannelGroupListEvent(self, schid, channelGroupID, name, atype, iconID, saveDB):
            if self.toggle:
                if self.requested == True:
                    for _name in self.banned_names:
                        if name.upper().__contains__(_name): self.sbgroup = channelGroupID;break
                    for _name in self.mod_names:
                        if name.upper().__contains__(_name): self.smgroup = channelGroupID;break
                    for _name in self.admin_names:
                        if name.upper().__contains__(_name): self.sagroup = channelGroupID;break

        def onChannelGroupListFinishedEvent(self, schid):
            if self.toggle:
                self.requested = False;self.check = True

        def onClientChannelGroupChangedEvent(self, serverConnectionHandlerID, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):
            if not self.check: return False
            if self.toggle:
                (error, _clid) = ts3lib.getClientID(serverConnectionHandlerID)
                (error, _cid) = ts3lib.getChannelOfClient(serverConnectionHandlerID, _clid)
                if clientID == _clid:
                    if channelGroupID == self.sagroup:
                        if self.ownchannels.__contains__(channelID):
                            _t = False
                        else:
                            self.ownchannels.append(channelID)
                    elif channelGroupID == self.smgroup:
                        (error, neededTP) = ts3lib.getChannelVariableAsInt(serverConnectionHandlerID, _cid, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
                        if neededTP > 0:
                            (error, clients) = ts3lib.getChannelClientList(serverConnectionHandlerID, _cid)
                            for client in clients:
                                if client == _clid: continue
                                (error, _cgid) = ts3lib.getClientVariableAsInt(serverConnectionHandlerID, client, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
                                if _cgid == self.sagroup: continue
                                (error, uid) = ts3lib.getClientVariableAsString(serverConnectionHandlerID, client, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                                if self.InContacts(uid) == 0:
                                    ts3lib.requestClientSetIsTalker(serverConnectionHandlerID, client, True)
                elif channelID == _cid and channelGroupID == self.sbgroup:
                    #(error, uid) = ts3lib.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                    (error, _cid) = ts3lib.getChannelOfClient(serverConnectionHandlerID, clientID)
                    if _cid in self.ownchannels:
                        if not self.reason == "": ts3lib.requestClientKickFromChannel(serverConnectionHandlerID, clientID, "Banned by \"%s\" for %s"%invokerName,self.reason);self.reason = ""
                        else: ts3lib.requestClientKickFromChannel(serverConnectionHandlerID, clientID, "You were banned by \"%s\""%invokerName)

        def onClientMoveEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moveMessage):
            if not self.check: return False
            if self.toggle:
                (error, _clid) = ts3lib.getClientID(serverConnectionHandlerID)
                (error, _cid) = ts3lib.getChannelOfClient(serverConnectionHandlerID, _clid)
                (error, _cgid) = ts3lib.getClientVariableAsInt(serverConnectionHandlerID, _clid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
                if not clientID == _clid:
                    (error, uid) = ts3lib.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                    if oldChannelID == 0: self.checkUser(uid) # and _cgid == self.smgroup or _cgid == self.sagroup
                    if newChannelID == _cid and _cgid == self.smgroup:
                        (error, neededTP) = ts3lib.getChannelVariableAsInt(serverConnectionHandlerID, _cid, ts3defines.ChannelPropertiesRare.CHANNEL_NEEDED_TALK_POWER)
                        if neededTP > 0:
                            if self.InContacts(uid) == 0: ts3lib.requestClientSetIsTalker(serverConnectionHandlerID, clientID, True)

        def onClientMoveSubscriptionEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility):
            if not self.check: return False
            if self.toggle:
                (error, _clid) = ts3lib.getClientID(serverConnectionHandlerID)
                if clientID != _clid:
                    (error, uid) = ts3lib.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                    self.checkUser(uid)

        def onNewChannelCreatedEvent(self, serverConnectionHandlerID, channelID, channelParentID, invokerID, invokerName, invokerUniqueIdentifier):
            if not self.check: return False
            if self.toggle and self.autoCheckOnChannel:
                (error, _clid) = ts3lib.getClientID(serverConnectionHandlerID)
                if invokerID == _clid:
                    self.checkAllUsers()

        def onDelChannelEvent(self, serverConnectionHandlerID, channelID, invokerID, invokerName, invokerUniqueIdentifier):
            if not self.check: return False
            if self.toggle:
                if self.ownchannels.__contains__(channelID):
                    self.ownchannels.remove(channelID)

        def onClientDBIDfromUIDEvent(self, serverConnectionHandlerID, uniqueClientIdentifier, clientDatabaseID):
            if self.toggle:
                if self.check:
                    _cid = self.requestedC.pop(0)
                    if _cid == 0 and self.autoMod:
                        ts3lib.requestSetClientChannelGroup(serverConnectionHandlerID, [self.smgroup for _, _ in enumerate(self.ownchannels)], self.ownchannels, [clientDatabaseID])
                        ts3lib.printMessageToCurrentTab("[color=green]Gave Client "+self.clientURL(serverConnectionHandlerID, None, uniqueClientIdentifier)+" Channel Mod in #"+str(self.ownchannels)+"[/color]")
                    elif _cid == 1 and self.autoBan:
                        ts3lib.requestSetClientChannelGroup(serverConnectionHandlerID, [self.sbgroup for _, _ in enumerate(self.ownchannels)], self.ownchannels, [clientDatabaseID])
                        ts3lib.printMessageToCurrentTab("[color=red]Banned Client "+self.clientURL(serverConnectionHandlerID, None, uniqueClientIdentifier)+" from Channels #"+str(self.ownchannels)+"[/color]")
                elif self.checkcurrent == uniqueClientIdentifier:
                    ts3lib.requestSetClientChannelGroup(serverConnectionHandlerID, [self.sbgroup for _, _ in enumerate(self.ownchannels)], self.ownchannels, [clientDatabaseID]); self.checkcurrent = ""
                    ts3lib.printMessageToCurrentTab("[color=orange]KickBanned Client "+self.clientURL(serverConnectionHandlerID, None, uniqueClientIdentifier)+" from Channels #"+str(self.ownchannels)+"[/color]")

        def onUpdateClientEvent(self, serverConnectionHandlerID, clientID, invokerID, invokerName, invokerUniqueIdentifier):
            if self.check and self.toggle:
                (error, _clid) = ts3lib.getClientID(serverConnectionHandlerID)
                if not clientID == _clid:
                    (error, _tcid) = ts3lib.getChannelOfClient(serverConnectionHandlerID, clientID)
                    if _tcid in self.ownchannels:
                        (error, _cgid) = ts3lib.getClientVariableAsInt(serverConnectionHandlerID, _clid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
                        if _cgid in [self.smgroup, self.sagroup]:
                            if self.checkRecording:
                                (error, clientRecStatus) = ts3lib.getClientVariableAsInt(serverConnectionHandlerID, clientID, ts3defines.ClientProperties.CLIENT_IS_RECORDING)
                                if clientRecStatus == 1:
                                    self.reason == "Recording"
                                    _schid = ts3lib.getCurrentServerConnectionHandlerID()
                                    self.requestedC.extend([1])
                                    _dbid = ts3lib.requestClientDBIDfromUID(_schid, uid)

        def onClientKickFromChannelEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentiﬁer, kickMessage):
            if not self.autoBanOnKick: return False
            if self.toggle:
                (error, _clid) = ts3lib.getClientID(serverConnectionHandlerID)
                if not clientID == _clid:
                    (error, _cgid) = ts3lib.getClientVariableAsInt(serverConnectionHandlerID, _clid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
                    if _cgid == self.smgroup or _cgid == self.sagroup:
                        (error, _cid) = ts3lib.getChannelOfClient(serverConnectionHandlerID, _clid)
                        (error, uid) = ts3lib.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                        if oldChannelID == _cid and kickMessage == "": self.checkcurrent = uid;ts3lib.requestClientDBIDfromUID(serverConnectionHandlerID, uid)

except:
    try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0);pass
    except: pass
