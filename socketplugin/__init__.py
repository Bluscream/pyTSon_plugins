from ts3plugin import ts3plugin
from websocket import create_connection
import ts3lib, ts3defines, tshelp, json

class socketplugin(ts3plugin):
	"""docstring for overlayplugin"""
	name = "socket"
	requestAutoload = False
	version = "0.1"
	apiVersion = 21
	author = "Scratch"
	description = "Overlay helper"
	offersConfigure = False
	commandKeyword = ""
	infoTitle = ""
	menuItems = []
	hotkeys = []
	global currentActiveServer
	global ws
	

	def __init__(self):
		#Open Socket
		ts3lib.printMessageToCurrentTab("Connection Open")
		self.ws = create_connection("ws://localhost:8000/")
		self.ws.send(json.dumps({'debug': 'teamspeak connect'}))
		self.currentActiveServer = ts3lib.getCurrentServerConnectionHandlerID()
		self.ws.send(json.dumps({'event': 'updateChannelClients', 'clients': tshelp.getNearbyClients(self.currentActiveServer), 'channelName': tshelp.getChannelName(self.currentActiveServer,tshelp.getChannelID(self.currentActiveServer))}))


	def stop(self):
		#Close Socket
		self.ws.send(json.dumps({'debug': 'teamspeak disconnect'}))
		self.ws.close()
		ts3lib.printMessageToCurrentTab("Connection Closed")

	def onTalkStatusChangeEvent(self, serverConnectionHandlerID, status, isReceivedWhisper, clientID):
		name = ts3lib.getClientDisplayName(serverConnectionHandlerID, clientID)[1]
		if serverConnectionHandlerID == self.currentActiveServer:
			self.ws.send(json.dumps({'event': 'onTalkStatusChangeEvent', 'clientID': clientID, 'status': status}))

#			{'event': 'onTalkStatusChangeEvent', 'cilentID': clientID, 'status': status}

			# if status == ts3defines.TalkStatus.STATUS_TALKING:
			#	ts3lib.printMessageToCurrentTab("%s started talking" % name)
			#elif status == ts3defines.TalkStatus.STATUS_NOT_TALKING:
			#	ts3lib.printMessageToCurrentTab("%s stopped talking" % name)
			

	def onClientSelfVariableUpdateEvent(self, serverConnectionHandlerID, flag, oldValue, newValue):
		if flag == ts3defines.ClientProperties.CLIENT_INPUT_HARDWARE:
			self.currentActiveServer = serverConnectionHandlerID
#			{'event': 'onClientSelfVariableUpdateEvent', 'flag': flag, 'data': [oldValue, newValue]}
			self.ws.send(json.dumps({'event': 'ActiveServerSwap', 'serverConnectionHandlerID': serverConnectionHandlerID,'channelName': tshelp.getChannelName(serverConnectionHandlerID,tshelp.getChannelID(serverConnectionHandlerID)), 'serverName': tshelp.getServerName(serverConnectionHandlerID), 'clients': tshelp.getNearbyClients(self.currentActiveServer)}))
			
			#ts3lib.printMessageToCurrentTab("Switched Server Mic to %s" % tshelp.getServerName(serverConnectionHandlerID))
			

	def onClientMoveEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moveMessage):
		#Log Channel Change
		#ts3lib.printMessageToCurrentTab("Switched room from %s to %s" % (tshelp.getChannelName(serverConnectionHandlerID,oldChannelID), tshelp.getChannelName(serverConnectionHandlerID,newChannelID)))
		if self.currentActiveServer == serverConnectionHandlerID and clientID == ts3lib.getClientID(serverConnectionHandlerID)[1]: #If User Moves
			self.ws.send(json.dumps({'event': 'onClientMoveEvent', 'channelID' : newChannelID, 'channelName': tshelp.getChannelName(serverConnectionHandlerID,newChannelID), 'clients': tshelp.getNearbyClients(self.currentActiveServer)}))
#			self.ws.send(json.dumps({'event': 'updateChannelClients', 'clients': tshelp.getNearbyClients(self.currentActiveServer)}))
	#		updateChannelClients()
		elif self.currentActiveServer == serverConnectionHandlerID and clientID != ts3lib.getClientID(serverConnectionHandlerID)[1] and (tshelp.getChannelID(serverConnectionHandlerID) == oldChannelID or tshelp.getChannelID(serverConnectionHandlerID) == newChannelID):
			EVENT = 0
			if tshelp.getChannelID(serverConnectionHandlerID) == newChannelID:
				EVENT = 0
			else:
				EVENT = 1
			self.ws.send(json.dumps({'event': 'nearbyClientMoveEvent', 'client': tshelp.getClientInfo(serverConnectionHandlerID, clientID), 'status': EVENT}))

	def onClientMoveTimeoutEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, timeoutMessage):
		if self.currentActiveServer == serverConnectionHandlerID and oldChannelID == tshelp.getChannelID(serverConnectionHandlerID):
			self.ws.send(json.dumps({'event': 'nearbyClientMoveEvent', 'client': tshelp.getClientInfo(serverConnectionHandlerID, clientID), 'status': 1}))	

	
	def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
		#if newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
		if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTED:
			self.currentActiveServer = serverConnectionHandlerID
			self.ws.send(json.dumps({'event': 'ActiveServerSwap', 'serverConnectionHandlerID': serverConnectionHandlerID,'channelName': tshelp.getChannelName(serverConnectionHandlerID,tshelp.getChannelID(serverConnectionHandlerID)), 'serverName': tshelp.getServerName(serverConnectionHandlerID), 'clients': tshelp.getNearbyClients(self.currentActiveServer)}))

	def onClientDisplayNameChanged(self, serverConnectionHandlerID, clientID, displayName, uniqueClientIdentifier):
		if self.currentActiveServer == serverConnectionHandlerID:
			self.ws.send(json.dumps({'event': 'onClientDisplayNameChanged', 'client':[clientID, displayName]}))

	def onClientKickFromServerEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
		if self.currentActiveServer == serverConnectionHandlerID and oldChannelID == tshelp.getChannelID(serverConnectionHandlerID):
			self.ws.send(json.dumps({'event': 'nearbyClientMoveEvent', 'client': tshelp.getClientInfo(serverConnectionHandlerID, clientID), 'status': 1}))

	def onClientMoveMovedEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
		if self.currentActiveServer == serverConnectionHandlerID and oldChannelID == tshelp.getChannelID(serverConnectionHandlerID):
			self.ws.send(json.dumps({'event': 'nearbyClientMoveEvent', 'client': tshelp.getClientInfo(serverConnectionHandlerID, clientID), 'status': 1}))	