import ts3lib
try:
    import ts3defines
    from datetime import datetime
    from ts3plugin import ts3plugin
    from urllib.parse import quote as urlencode
    from configparser import ConfigParser
    from os import path

    class welcomeBot(ts3plugin):
        name = "Welcome Bot"
        try: apiVersion = pytson.getCurrentApiVersion()
  except: apiVersion = 22
        requestAutoload = False
        version = "1.0"
        author = "Bluscream"
        description = "Welcome Bot."
        offersConfigure = False
        commandKeyword = ""
        infoTitle = None
        menuItems = []
        hotkeys = []
        debug = False
        enabled = False
        default = 0
        ini = path.join(pytson.getPluginPath(), "scripts", __name__, "settings.ini")
        cfg = ConfigParser()
        cfg.optionxform = str
        #tmp = []
        update = 0

        def __init__(self):
            if path.isfile(self.ini): self.cfg.read(self.ini)
            else:
                self.cfg['QTRtPmYiSKpMS8Oyd4hyztcvLqU='] = {
                    "US": "Welcome, {nick}\n"+
                        "To get verified on this Teamspeak 3 Server you need to follow this steps:\n\n"+
                        "1. Join the minecraft server [color=green]gommehd.net[/color].\n"+
                        "2. Send [color=red]/ts set {uid}[/color] in the minecraft chat.\n"+
                        "3. Message the user [URL=client://0/serveradmin~Gomme-Bot]Gomme-Bot[/URL] in Teamspeak and send them your Minecraft Nickname (Proper casing is important)\n"+
                        "4. If the registration succeeded the server group \"Registriert\" will be assigned to you. It can take a while for your skin head to appear behind your TS name.\n\n"+
                        "Please consider this teamspeak mostly german, so don't expect everyone to speak proper english.\n"+
                        "[color=red]Raids and Trolling will result in bans.[/color]\n"+
                        "After you got registered you get access to the support channels to get help whenever you need some.\n\n"+
                        "Enjoy your stay :)",
                    "DE": "Willkommen, {nick}\n"+
                        "Um dich auf diesem Teamspeak Server zu registrieren musst du folgendes tun:\n\n"+
                        "1. Auf den Minecraft Server [color=green]gommehd.net[/color] joinen.\n"+
                        "2. In den Minecraft chat [color=red]/ts set {uid}[/color] eingeben.\n"+
                        "3. Im Teamspeak Chat dem User [URL=client://0/serveradmin~Gomme-Bot]Gomme-Bot[/URL] deinen Minecraft Namen schreiben (Gross/Kleinschreibung beachten)\n"+
                        "4. Wenn die Registrierung erfolgreich warst erhaelst du die Server Gruppe \"Registriert\". Es kann eine Zeit lang dauern bis dein Minecraft Kopf hinter deinem Namen erscheint.\n\n"+
                        "Bitte bedenke das du auf diesem Teamspeak mit wildfremden Leuten redest ueber die du nichts weisst.\n"+
                        "[color=red]Fuer deine eigene Sicherheit achte bitte darauf an wen du welche Informationen ueber dich rausgibst![/color]\n\n"+
                        #"Dinge wie private Bilder werden von einigen Personen gerne weitergegeben!\n\n"+
                        "Für Info's und Rueckfragen zum [url=https://github.com/Bluscream/pyTSon_plugins/blob/master/scripts/welcomeBot/__init__.py]Bot[/url] bitte [URL=client://0/x63jNGEr/PXnu9l3bFECzMzWfXk=]TeamspeakUser[/URL] kontaktieren.\n\n"+
                        "Viel Spass dann :)",
                    "AT": "Willkommen, {nick}\n"+
                        "Um dich auf diesem Teamspeak Server zu registrieren musst du folgendes tun:\n\n"+
                        "1. Auf den Minecraft Server [color=green]gommehd.net[/color] joinen.\n"+
                        "2. In den Minecraft chat [color=red]/ts set {uid}[/color] eingeben.\n"+
                        "3. Im Teamspeak Chat dem User [URL=client://0/serveradmin~Gomme-Bot]Gomme-Bot[/URL] deinen Minecraft Namen schreiben (Gross/Kleinschreibung beachten)\n"+
                        "4. Wenn die Registrierung erfolgreich warst erhaelst du die Server Gruppe \"Registriert\". Es kann eine Zeit lang dauern bis dein Minecraft Kopf hinter deinem Namen erscheint.\n\n"+
                        "Bitte bedenke das du auf diesem Teamspeak mit wildfremden Leuten redest ueber die du nichts weisst.\n"+
                        "[color=red]Fuer deine eigene Sicherheit achte bitte darauf an wen du welche Informationen ueber dich rausgibst![/color]\n\n"+
                        "Für Info's und Rueckfragen zum [url=https://github.com/Bluscream/pyTSon_plugins/blob/master/scripts/welcomeBot/__init__.py]Bot[/url] bitte [URL=client://0/x63jNGEr/PXnu9l3bFECzMzWfXk=]TeamspeakUser[/URL] kontaktieren.\n\n"+
                        #"Dinge wie private Bilder werden von einigen Personen gerne weitergegeben!\n\n"+
                        "Viel Spass dann :)",
                    "CH": "Willkommen, {nick}\n"+
                        "Um dich auf diesem Teamspeak Server zu registrieren musst du folgendes tun:\n\n"+
                        "1. Auf den Minecraft Server [color=green]gommehd.net[/color] joinen.\n"+
                        "2. In den Minecraft chat [color=red]/ts set {uid}[/color] eingeben.\n"+
                        "3. Im Teamspeak Chat dem User [URL=client://0/serveradmin~Gomme-Bot]Gomme-Bot[/URL] deinen Minecraft Namen schreiben (Gross/Kleinschreibung beachten)\n"+
                        "4. Wenn die Registrierung erfolgreich warst erhaelst du die Server Gruppe \"Registriert\". Es kann eine Zeit lang dauern bis dein Minecraft Kopf hinter deinem Namen erscheint.\n\n"+
                        "Bitte bedenke das du auf diesem Teamspeak mit wildfremden Leuten redest ueber die du nichts weisst.\n"+
                        "[color=red]Fuer deine eigene Sicherheit achte bitte darauf an wen du welche Informationen ueber dich rausgibst![/color]\n\n"+
                        "Für Info's und Rueckfragen zum [url=https://github.com/Bluscream/pyTSon_plugins/blob/master/scripts/welcomeBot/__init__.py]Bot[/url] bitte [URL=client://0/x63jNGEr/PXnu9l3bFECzMzWfXk=]TeamspeakUser[/URL] kontaktieren.\n\n"+
                        #"Dinge wie private Bilder werden von einigen Personen gerne weitergegeben!\n\n"+
                        "Viel Spass dann :)"
                }
                with open(self.ini, 'w') as configfile:
                    self.cfg.write(configfile)
            schid = ts3lib.getCurrentServerConnectionHandlerID()
            self.default = self.getDefaultChannel(schid)
            ts3lib.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
            if self.debug: ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

        def clientURL(self, schid=None, clid=1, uid=None, nickname=None, encodednick=None):
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

        def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
            if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
                (error, suid) = ts3lib.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
                if self.cfg.has_section(suid): self.default == self.getDefaultChannel(schid)
            elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED: self.default = 0

        def getDefaultChannel(self, schid):
            (error, clist) = ts3lib.getChannelList(schid)
            for c in clist:
                (error, default) = ts3lib.getChannelVariableAsInt(schid, c, ts3defines.ChannelProperties.CHANNEL_FLAG_DEFAULT)
                if default: return c

        def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
            if self.debug: ts3lib.printMessageToCurrentTab("oldChannelID: {0}".format(oldChannelID))
            if not oldChannelID == 0: return
            (error, _clid) = ts3lib.getClientID(schid)
            if self.debug: ts3lib.printMessageToCurrentTab("_clid: {0} | clientID: {1}".format(_clid,clientID))
            if clientID == _clid: return
            if self.debug: ts3lib.printMessageToCurrentTab("newChannelID: {0} | self.default: {1}".format(newChannelID,self.default))
            if not newChannelID == self.default: return
            #(error, uid) = ts3lib.getClientVariableAsString(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            #if self.debug: ts3lib.printMessageToCurrentTab("uid: {0} | self.tmp: {1}".format(uid,self.tmp))
            #if uid in self.tmp: return
            (error, suid) = ts3lib.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
            if self.debug: ts3lib.printMessageToCurrentTab("suid: {0} | self.cfg.sections(): {1} | self.cfg.has_section(suid): {2}".format(suid,self.cfg.sections(),self.cfg.has_section(suid)))
            if not self.cfg.has_section(suid): return
            self.update = clientID
            ts3lib.requestClientVariables(schid, clientID)

        def onUpdateClientEvent(self, schid, clientID, invokerID, invokerName, invokerUniqueIdentiﬁer):
            try:
                if not self.update == clientID: return
                self.update = 0
                (error, connects) = ts3lib.getClientVariableAsUInt64(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_TOTALCONNECTIONS)
                (error, uid) = ts3lib.getClientVariableAsString(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                if self.debug: ts3lib.printMessageToCurrentTab("error: {0} | connects: {1} | uid: {2}".format(error,connects,uid))
                if connects > 1 and not uid == "x63jNGEr/PXnu9l3bFECzMzWfXk=": return
                (error, suid) = ts3lib.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
                (error, country) = ts3lib.getClientVariableAsString(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_COUNTRY)
                if self.debug: ts3lib.printMessageToCurrentTab("error: {0} | country: {1}".format(error,country))
                msg = self.cfg.get(suid, country, fallback=self.cfg.get(suid, 'US'))
                if '{nick}' in msg: msg = msg.replace('{nick}', self.clientURL(schid, clientID, uid))
                if '{country}' in msg: msg = msg.replace('{country}', country)
                if '{cid}' in msg: msg = msg.replace('{cid}', clientID)
                if '{uid}' in msg: msg = msg.replace('{uid}', uid)
                if '{connects}' in msg: msg = msg.replace('{connects}', connects)
                msg = [msg[i:i + 1024] for i in range(0, len(msg), 1024)]
                for message in msg: ts3lib.requestSendPrivateTextMsg(schid, "{0}".format(message), clientID)
                (error, ownid) = ts3lib.getClientID(schid)
                (error, _uid) = ts3lib.getClientVariableAsString(schid, ownid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                ts3lib.clientChatClosed(schid, uid, clientID)
                ts3lib.printMessageToCurrentTab("Sent client {0} the welcome message for {1}".format(clientID,suid))
                #self.tmp.extend([uid]);
            except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0);pass

except:
    try: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0);pass
    except: pass
