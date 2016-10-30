from ts3plugin import ts3plugin, PluginHost
import ts3, ts3defines, datetime


class notify(ts3plugin):
    name = "Notifier"
    apiVersion = 20
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Automatically notifies other clients about:\n\n○ Outdated Clients\n○ Unread Offline Messages.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle "+name, "")]
    hotkeys = []
    debug = False
    toggle = False
    requested = False
    checkOutdatedVersion = True
    checkUnreadMessages = True
    currentVersion = 1468491418
    currentVersion_ = "3.0.19.4"
    _sent = []

    def __init__(self):
        ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/Bluscream]Bluscream[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            self.toggle = not self.toggle
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.datetime.now())+" Set "+self.name+" to [color=yellow]"+str(self.toggle)+"[/color]")

    def onClientMoveEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if self.toggle:
            (error, _clid) = ts3.getClientID(serverConnectionHandlerID)
            if clientID != _clid and oldChannelID == 0:
                self.requested = True
                ts3.requestClientVariables(serverConnectionHandlerID, clientID)

    def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
        if self.toggle:
            if newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
                self._sent.clear()

    def onUpdateClientEvent(self, serverConnectionHandlerID, clientID, invokerID, invokerName, invokerUniqueIdentifier):
        if self.requested:
            self.requested = False
            (error, _uid) = ts3.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            if not self._sent.__contains__(_uid):
                return
            if self.checkOutdatedVersion:
                (error, targetVer) = ts3.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientProperties.CLIENT_VERSION)
                if error != ts3defines.ERROR_ok:
                    return
                ts3.printMessageToCurrentTab("targetVer: "+targetVer)
                targetVer = targetVer.split("Build: ")
                targetVer = targetVer[1]
                targetVer = int(targetVer.split("]")[0])
                if targetVer < self.currentVersion:
                    (error, country) = ts3.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientPropertiesRare.CLIENT_COUNTRY)
                    if country == "DE" or country == "CH" or country == "AT":
                        ts3.requestSendPrivateTextMsg(serverConnectionHandlerID, "[color=red]Hinweis[/color]:\n\nDu nutzt eine veraltete Version von Teamspeak.\nBitte aktualisiere deinen Client auf Version [color=blue]"+self.currentVersion_+"[/color]", clientID)
                        self._sent.extend([_uid])
                    else:
                        ts3.requestSendPrivateTextMsg(serverConnectionHandlerID, "[color=red]Attention[/color]:\n\nYou are using an outdated Teamspeak.\nPlease update your Client to Version [color=blue]"+self.currentVersion_+"[/color]", clientID)
                        self._sent.extend([_uid])
            if self.checkUnreadMessages:
                (error, platform) = ts3.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientProperties.CLIENT_PLATFORM)
                if platform != "Android" and platform != "iOS":
                    (error, messages) = ts3.getClientVariableAsInt(serverConnectionHandlerID, clientID, ts3defines.ClientPropertiesRare.CLIENT_UNREAD_MESSAGES)
                    ts3.printMessageToCurrentTab("messages: "+str(messages))
                    if messages > 1:
                        (error, country) = ts3.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientPropertiesRare.CLIENT_COUNTRY)
                        ts3.printMessageToCurrentTab("country: "+country)
                        if country == "DE" or country == "CH" or country == "AT":
                            ts3.requestSendPrivateTextMsg(serverConnectionHandlerID, "[color=orange]Hinweis[/color]:\n\nDu hast [color=blue]eine[/color] ungelesene Offline Nachricht.\nDu kannst sie nachlesen indem du auf \"Extras\" => \"Offline Nachrichten\" klickst oder einfach [STRG]+[O] auf deiner Tastatur drückst.", clientID)
                            self._sent.extend([_uid])
                        else:
                            ts3.requestSendPrivateTextMsg(serverConnectionHandlerID, "[color=orange]Reminder[/color]:\n\nYou have [color=blue]eine[/color] unread offline message.\nYou can read it by clicking on \"Tools\" => \"Offline Messages\" or pressing [CTRL]+[O] on your keyboard.", clientID)
                            self._sent.extend([_uid])
                    elif messages == 1:
                        (error, country) = ts3.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientPropertiesRare.CLIENT_COUNTRY)
                        if country == "DE" or country == "CH" or country == "AT":
                            ts3.requestSendPrivateTextMsg(serverConnectionHandlerID, "[color=orange]Hinweis[/color]:\n\nDu hast [color=blue]"+str(messages)+"[/color] ungelesene Offline Nachrichten.\nDu kannst sie nachlesen indem du auf \"Extras\" => \"Offline Nachrichten\" klickst oder einfach [STRG]+[O] auf deiner Tastatur drückst.", clientID)
                            self._sent.extend([_uid])
                        else:
                            ts3.requestSendPrivateTextMsg(serverConnectionHandlerID, "[color=orange]Reminder[/color]:\n\nYou have [color=blue]"+str(messages)+"[/color] unread offline messages.\nYou can read them by clicking on \"Tools\" => \"Offline Messages\" or pressing [CTRL]+[O] on your keyboard.", clientID)
                            self._sent.extend([_uid])
