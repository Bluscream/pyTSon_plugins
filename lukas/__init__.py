import ts3lib as ts3; from ts3plugin import ts3plugin, PluginHost
import ts3lib as ts3; import   ts3defines
from PythonQt.QtGui import *
from PythonQt.QtCore import *
from PythonQt.QtSql import QSqlDatabase

class luemmelspluginpack(ts3plugin):
	name = "Luemmels Pluginpack"
	requestAutoload = False
	version = "1.0"
	apiVersion = 22
	author = "Luemmel"
	description = "Autokicker, Linkinfo, Autochannelgroup"
	offersConfigure = False
	commandKeyword = ""
	infoTitle = None
	hotkeys = []
	autokick_label = "Automatischer kick nach Channel-Bann"
	linkinfo_label = "Linkinfo"
	freunde_label = "Freunden automatisch Operator geben"
	blockierte_label = "Blockierten Usern Channel-Bann geben"
	menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "===============================", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "=== "+autokick_label, ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "On/Off", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 3, "=== "+linkinfo_label, ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 4, "On/Off", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 5, "=== "+freunde_label, ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 6, "On/Off", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 7, "=== "+blockierte_label, ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 8, "On/Off", ""),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 9, "===============================", "")]
	gommeuid = "QTRtPmYiSKpMS8Oyd4hyztcvLqU="
	aktiviert = "[color=green]aktiviert[/color]"
	deaktiviert = "[color=red]deaktiviert[/color]"
	autokick = True
	linkinfo = True
	freunde = True
	blockierte = True
	dlg = None

	def __init__(self):
		self.db = QSqlDatabase.addDatabase("QSQLITE","pyTSon_contacts")
		self.db.setDatabaseName(ts3.getConfigPath() + "settings.db")
		if not self.db.isValid(): raise Exception("Datenbank ungültig")
		if not self.db.open(): raise Exception("Datenbank konnte nicht geöffnet werden")
		ts3.printMessageToCurrentTab("\n[color=orange]"+self.name+"[/color]")
		ts3.printMessageToCurrentTab(self.autokick_label+" "+self.aktiviert)
		ts3.printMessageToCurrentTab(self.linkinfo_label+" "+self.aktiviert)
		ts3.printMessageToCurrentTab(self.freunde_label+" "+self.aktiviert)
		ts3.printMessageToCurrentTab(self.blockierte_label+" "+self.aktiviert)

	def stop(self):
		self.db.close();self.db.delete()
		QSqlDatabase.removeDatabase("pyTSon_contacts")
		ts3.printMessageToCurrentTab("\n[color=orange]"+self.name+"[/color] wurde "+self.deaktiviert)

	def contactStatus(self, uid):
		q = self.db.exec_("SELECT * FROM contacts WHERE value LIKE '%%IDS=%s%%'" % uid)
		ret = 2
		if q.next():
			val = q.value("value")
			for l in val.split('\n'):
				if l.startswith('Friend='):
					ret = int(l[-1])
		q.delete();return ret

	def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
		if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
			if menuItemID == 2:
				self.autokick = not self.autokick
				if self.autokick == True: ts3.printMessageToCurrentTab(self.autokick_label+" "+self.aktiviert)
				else: ts3.printMessageToCurrentTab(self.autokick_label+" "+self.deaktiviert)
				if not self.dlg: self.dlg = QDialog()
				self.dlg.show()
			if menuItemID == 4:
				self.linkinfo = not self.linkinfo
				if self.linkinfo == True: ts3.printMessageToCurrentTab(self.linkinfo_label+" "+self.aktiviert)
				else: ts3.printMessageToCurrentTab(self.linkinfo_label+" "+self.deaktiviert)
			if menuItemID == 6:
				self.linkinfo = not self.linkinfo
				if self.linkinfo == True: ts3.printMessageToCurrentTab(self.freunde_label+" "+self.aktiviert)
				else: ts3.printMessageToCurrentTab(self.freunde_label+" "+self.deaktiviert)
			if menuItemID == 8:
				self.linkinfo = not self.linkinfo
				if self.linkinfo == True: ts3.printMessageToCurrentTab(self.blockierte_label+" "+self.aktiviert)
				else: ts3.printMessageToCurrentTab(self.blockierte_label+" "+self.deaktiviert)

	def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
		#ServerUID abfragen
		(error, suid) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)

		#Wenn ServerUID von Gomme und wenn Freunde oder Blockierte Funktion aktiviert
		if suid == self.gommeuid and (self.freunde == True or self.blockierte == True):

			#Meine Client und ChannelID
			(error, myid) = ts3.getClientID(schid)
			(error, mych) = ts3.getChannelOfClient(schid, myid)

			#Wenn User in mein Cahnnel joint
			if newChannelID == mych:

				#UID des Users abfragen
				(error, uid) = ts3.getClientVariableAsString(schid, clientID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)

				#Freundschaftsstatus des Users abfragen
				f = self.contactStatus(uid)

				#Aktuelle Channelgruppe des gejointen Users abfragen
				(error, gid) = ts3.getClientVariableAsInt(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)

				#Meine aktuelle Channelgruppe abfragen
				(error, mygid) = ts3.getClientVariableAsInt(schid, myid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)

				#Wenn geblockter User und Funktion aktiviert und ich C oder O bin
				if f == 1 and self.freunde == True and (mygid == 10 or mygid == 11):
					(error, dbid) = ts3.getClientVariableAsUInt64(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
					ts3.requestSetClientChannelGroup(schid, [12], [mych], [dbid])
					ts3.requestClientKickFromChannel(schid, clientID, "Geblockter User")
					ts3.requestSendPrivateTextMsg(schid, 'Ihhhhh ein geblockter User. Weg mit ihm!!! Bringt ihn zum Scheiterhaufen', clientID)

				#Wenn Freund und Funktion aktiviert und ich C bin und User nicht schon O hat
				if f == 0 and self.blockierte == True and mygid == 10 and not gid == 11:
					(error, dbid) = ts3.getClientVariableAsUInt64(schid, clientID, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
					ts3.requestSetClientChannelGroup(schid, [11], [mych], [dbid])

	def onClientChannelGroupChangedEvent(self, schid, channelGroupID, channelID, clientID, invokerClientID, invokerName, invokerUniqueIdentity):

		#ServerUID abfragen
		(error, suid) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)

		#Wenn autokick aktiviert und ServerUID von Gomme
		if self.autokick == True and suid == self.gommeuid:

			#Meine ClientID und ChannelID
			(error, myid) = ts3.getClientID(schid)
			(error, mych) = ts3.getChannelOfClient(schid, myid)

			#Meine aktuelle Channelgruppe abfragen
			(error, mygid) = ts3.getClientVariableAsInt(schid, myid, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)


			#Wenn in meinem Channel ein Channel-Bann verteilt wurde und ich O oder C bin
			if mych == channelID and channelGroupID == 12 and (mygid == 10 or mygid == 11):

				#Client kicken und nette Nachricht senden
				ts3.requestClientKickFromChannel(schid, clientID, "Geblockter User")
				ts3.requestSendPrivateTextMsg(schid, 'Du wurdest mit einem Channel-Bann von mir oder jeemand anderem versehen. Ich habe dich in beiden Fällen gekickt.', clientID)

	def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
		if self.linkinfo == True:
			(error, myid) = ts3.getClientID(schid)
			(error, mych) = ts3.getChannelOfClient(schid, myid)

			if not myid == fromID and message.find("[URL]ts3server://") == -1 and (not message.find("[URL]") == -1 or not message.find("[url=") == -1 or not message.find("[URL=") == -1):
				start = message.find("[URL]")

				if not start == -1:
					end = message.find("[/URL]")
					message = message[start:end]
					message = message.replace("[URL]", "")
					oldmsg = message
				else:
					start = message.find("[URL=")
					cache = start

					if start == -1:
						start = message.find("[url=")

					end = message.find("]")
					message = message[start:end]

					if cache == -1:
						message = message.replace("[url=", "")
					else:
						message = message.replace("[URL=", "")

					oldmsg = message


				message = oldmsg+" -> [url=http://www.getlinkinfo.com/info?link="+message+"]Linkinfo[/url]"
				#ts3.printMessage(schid, message, 1)

				if targetMode == 1:
					ts3.requestSendPrivateTextMsg(schid, message, fromID)
				if targetMode == 2:
					ts3.requestSendChannelTextMsg(schid, message, mych)
