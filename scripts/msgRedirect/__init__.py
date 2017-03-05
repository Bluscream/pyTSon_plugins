import ts3lib, ts3defines, datetime
from ts3plugin import ts3plugin
from os import path


class msgRedirect(ts3plugin):
    name = "MSG Redirect"
    apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Manage your channel subscriptions the way YOU want."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = True
    infoMSG1 = "\n\nHallo [color=green]",
    infoMSG2 = "[/color], du bist hier [color=red]Gast[/color] aber moechtest trozdem im Channel mitschreiben?\n\nDann schreib mir einfach zurueck und ich werde die Nachricht an den Channel weiterleiten.\n\n[color=red]INFO: SPAM ODER SONSTIGER ABUSE WIRD MIT SOFORTIGEM CHANNELBAN UND BLOCK BESTRAFT![/color]",
    redirectMSG = "Weitergeleitete Nachricht von",
    BadWordArray = { 'hurensohn', 'ddos', 'wichser', 'egal', 'lizard', 'asshole', 'arschloch', 'fick', 'anus', 'scheide', 'vagina', 'fotze', 'schlampe', 'hitler', 'adolf', 'sieg', 'heil' }
    LinkArray = { '%://', 'www%.', '%.net', '%.de', '%.com', '%.me', '%.tk' }

    def __init__(self):
        ts3lib.logMessage(self.name + " script for pyTSon by " + self.author + " loaded from \"" + __file__ + "\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.debug: ts3lib.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format( datetime.datetime.now()) + " [color=orange]" + self.name + "[/color] Plugin for pyTSon by [url=https://github.com/" + self.author + "]" + self.author + "[/url] loaded.")

    def msgredirect(serverConnectionHandlerID, mode):
        if isempty(mode) then
            if MSGRedirect.var.ENABLED == true then
                MSGRedirect.var.ENABLED = false
                ts3lib.printMessageToCurrentTab("MSGRedirect set to \"FALSE\"")
            else
                MSGRedirect.var.ENABLED = true
                ts3lib.printMessageToCurrentTab("MSGRedirect set to \"TRUE\"")
            end
        else
            mode = string.lower(mode)
            if mode == "on" then
                MSGRedirect.var.ENABLED = true
                ts3lib.printMessageToCurrentTab("MSGRedirect set to \"TRUE\"")
            elseif mode == "off" then
                MSGRedirect.var.ENABLED = false
                ts3lib.printMessageToCurrentTab("MSGRedirect set to \"FALSE\"")

    def onClientMoveEvent(serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if MSGRedirect.var.ENABLED == true and MSGRedirect.var.LAST ~= clientID then
            ownID = ts3lib.getClientID(serverConnectionHandlerID)
            ownChannelID = ts3lib.getChannelOfClient(serverConnectionHandlerID, ownID)
            if newChannelID == ownChannelID and clientID ~= ownID then
                local clientServerGroups = ts3lib.getClientVariableAsString(serverConnectionHandlerID,clientID,34)
                if string.find(clientServerGroups, MSGRedirect.var.guestChannelGroup) then
                    MSGRedirect.var.LAST = clientID
                    clientName = ts3lib.getClientVariableAsString(serverConnectionHandlerID,clientID,ts3defs.ClientProperties.CLIENT_NICKNAME)
                    ts3lib.requestSendPrivateTextMsg(serverConnectionHandlerID, MSGRedirect.loc.infoMSG1 .. clientName .. MSGRedirect.loc.infoMSG2, clientID)

    def onTextMessageEvent(serverConnectionHandlerID, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        ownID = ts3lib.getClientID(serverConnectionHandlerID)
        ownChannelID = ts3lib.getChannelOfClient(serverConnectionHandlerID, ownID)
        clientChannelID = ts3lib.getChannelOfClient(serverConnectionHandlerID, fromID)
        clientChannelGroup = ts3lib.getClientVariableAsString(serverConnectionHandlerID,fromID,ts3defs.ClientProperties.CLIENT_CHANNEL_GROUP_ID)
        ownChannelGroupID = ts3lib.getClientVariableAsString(serverConnectionHandlerID,ownID,ts3defs.ClientProperties.CLIENT_CHANNEL_GROUP_ID)
        clientServerGroups = ts3lib.getClientVariableAsString(serverConnectionHandlerID,fromID,ts3defs.ClientProperties.CLIENT_SERVERGROUPS)
        if MSGRedirect.var.ENABLED == true and toID == ownID and clientChannelID == ownChannelID and ffIgnored == 0 then
            if ownChannelGroupID == MSGRedirect.var.channelMSGGroup or ownChannelGroupID == MSGRedirect.var.channelModGroup or ownChannelGroupID == MSGRedirect.var.channelAdminGroup then
                if clientChannelGroup ~= MSGRedirect.var.banChannelGroup and clientChannelGroup == MSGRedirect.var.guestChannelGroup and string.find(clientServerGroups, MSGRedirect.var.guestServerGroup ) then
                    lowMessage = string.lower(message)
                    if lowMessage ~= oldMSG and string.len(lowMessage) > 1 and string.len(lowMessage) < 850 then
                        local clientName = ts3lib.getClientVariableAsString(serverConnectionHandlerID,fromID,ts3defs.ClientProperties.CLIENT_NICKNAME)
                        if string.find (lowMessage, "ts3server:" ) ~= nil then
                            ScriptLog(clientName .. " hat versucht einen TS3Server Link zu versenden.")
                        elseif string.find (lowMessage, '%d+%.%d+%.%d+%.%d') ~= nil or string.find (lowMessage, '%w%w%w%w::%w%w%w%w::%w%w%w%w::%w%w%w%w') ~= nil or string.find (lowMessage, '%w%w%w%w:%w%w%w%w:%w%w%w%w:%w%w%w%w:%w%w%w%w:%w%w%w%w:%w%w%w%w:%w%w%w%w') ~= nil then
                            ScriptLog(clientName .. " hat versucht eine IP zu versenden.")
                        -- elseif then
                            -- ScriptLog(clientName .. " hat versucht eine IP zu versenden.")
                        else
                            local uniqueID = ts3lib.getClientVariableAsString(serverConnectionHandlerID,fromID,ts3defs.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                            local nickNameEncoded = urlencode(clientName)
                            ts3lib.requestSendChannelTextMsg(serverConnectionHandlerID, MSGRedirect.loc.redirectMSG .. " [URL=client://" .. fromID .. "/" .. uniqueID .. "~" .. nickNameEncoded .. "]\"" .. clientName .. "\"[/url]: " .. message, clientChannelID)
                            oldMSG = lowMessage

    def onDelChannelEvent(serverConnectionHandlerID, channelID, invokerID, invokerName, invokerUniqueIdentifier):
    -- ts3lib.printMessageToCurrentTab("onDelChannelEvent")
        local ownID = ts3lib.getClientID(serverConnectionHandlerID)
        local ownChannelID = ts3lib.getChannelOfClient(serverConnectionHandlerID, ownID)
        if channelID == ownChannelID then
            MSGRedirect.var.ENABLED = false
            ts3lib.printMessageToCurrentTab("[color=red]MSGRedirect was forced to shut down because our channel was deleted by "..invokerName.."![/color]")

    def onClientKickFromChannelEvent(serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        -- ts3lib.printMessageToCurrentTab("onClientKickFromChannelEvent")
        local ownID = ts3lib.getClientID(serverConnectionHandlerID)
        if ownID == clientID and MSGRedirect.var.ENABLED == true then
            clientMoveReq, error = ts3lib.requestClientMove(serverConnectionHandlerID, clientID, oldChannelID, "")
            if error ~= ts3errors.ERROR_ok then
                MSGRedirect.var.ENABLED = false
                ts3lib.printMessageToCurrentTab("[color=red]MSGRedirect was forced to shut down because we were unable to rejoin old channel" .. oldChannelID .. "![/color]")
                return
