from ts3plugin import ts3plugin, PluginHost
import ts3, ts3defines, datetime, configparser, os.path
from PythonQt.QtGui import QDialog, QInputDialog, QMessageBox, QWidget
from pytsonui import getValues, ValueType
from collections import OrderedDict

class info(ts3plugin):
    name = "Extended Info"
    apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Shows you more informations.\nBest to use together with a Extended Info Theme.\nClick on \"Settings\" to select what items you want to see :)\n\nHomepage: https://github.com/Bluscream/Extended-Info-Plugin\n\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = True
    commandKeyword = "info"
    infoTitle = "[b]"+name+":[/b]"
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Set Meta Data", "")]
    hotkeys = []
    ini = os.path.join(ts3.getConfigPath(), "extended_info.ini")
    config = configparser.ConfigParser()

    def __init__(self):
        if os.path.isfile(self.ini):
            self.config.read(self.ini)
            # self.SERVER = config['SERVER'].items()
            # self.CHANNEL = config['CHANNEL'].items()
            # self.CLIENT = config['CLIENT'].items()
        else:
            self.config['GENERAL'] = { "Debug": "False", "Colored": "False" }
            self.config['SERVER'] = {
                "Last Requested": "True", "Name": "False", "Server Connection Handler ID": "False", "Version": "False", "Platform": "False", "Clients": "False", "Channels": "False", "Connections": "False", "Uptime": "False", "Address": "False", "Resolved IP": "False",
                "Icon ID": "False", "License": "False", "UID": "False", "Virtualserver ID": "False", "Machine ID": "False", "Autostart": "False", "Password": "False", "Codec Encrypted": "False", "Default Groups": "False", "Max Bandwith": "False", "Banner": "False",
                "Hostbutton": "False", "Complaint Settings": "False", "Clients for forced Silence": "False", "Priority speaker dimm": "False", "Antiflood": "False", "Up/Download Quota": "False",
                "Month Bytes Transfered": "False", "Total Bytes Transfered": "False", "Needed Security Level": "False", "Log Settings": "False", "Min Client Version": "False", "Weblist Status": "False",
                "Privilege Key": "False", "Delete Channels after": "False", "IP": "True", "Created": "True", "Ping": "True", "Packet Loss": "True", "Ping": "True"
            }
            self.config['CHANNEL'] = {
                "Last Requested": "False", "Name": "False", "Phonetic Name": "False", "ID": "False", "Topic": "False", "Clients": "False", "Needed Talk Power": "False", "Order": "False", "Codec": "False", "Flags": "False", "Subscribed": "False",
                "Encrypted": "False", "Description": "False", "Icon ID": "False", "Delete Delay": "False", "Filepath": "False", "Forced Silence": "True", "Private": "True", "Latency": "True", "Security Salt": "True", "Password": "True"
            }
            self.config['CLIENT'] = {
                "Last Requested": "False", "Name": "False", "Phonetic Name": "False", "Version": "False", "Platform": "False", "Country": "False", "Client ID": "False", "Database ID": "False", "UID": "False", "Is Talking": "False", "Audio Status": "False",
                "Idle Time": "False", "Default Channel": "False", "Server Password": "False", "Volume Modifcator": "False", "Version Sign": "False", "Security Hash": "False", "Last Var Request": "False", "Login Credentials": "False",
                "Group ID's": "False", "First Connection": "False", "Last Connection": "False", "Total Connections": "False", "Away": "False", "Talk Power": "False", "Talk Power Request": "False", "Description": "False", "Is Talker": "False",
                "Month Bytes Transfered": "False", "Total Bytes Transfered": "False", "Is Priority Speaker": "False", "Unread Offline Messages": "False", "Needed ServerQuery View Power": "False", "Default Token": "False", "Meta Data": "False"
            }
            with open(self.ini, 'w') as configfile:
                self.config.write(configfile)
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.config['GENERAL']['Debug'] == "True":
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

    def configDialogClosed(self, r, vals):
        if r == QDialog.Accepted:
            ts3.printMessageToCurrentTab(str(vals))

    def configure(self, qParentWidget):
        d = dict()
        d['bool_debug'] = (ValueType.boolean, "Debug", self.config['GENERAL']['Debug'] == "True", None, None)
        d['bool_colored'] = (ValueType.boolean, "Colored InfoData", self.config['GENERAL']['colored'] == "True", None, None)
        d['list_server'] = (ValueType.listitem, "Server", ([key for key in self.config['SERVER']], [i for i, key in enumerate(self.config['SERVER']) if self.config['SERVER'][key] == "True"]), 0, 0)
        d['list_channel'] = (ValueType.listitem, "Channel", ([key for key in self.config['CHANNEL']], [i for i, key in enumerate(self.config['CHANNEL']) if self.config['CHANNEL'][key] == "True"]), 0, 0)
        d['list_client'] = (ValueType.listitem, "Client", ([key for key in self.config['CLIENT']], [i for i, key in enumerate(self.config['CLIENT']) if self.config['CLIENT'][key] == "True"]), 0, 0)
        ts3.printMessageToCurrentTab(str(d))
        widgets = getValues(None, "Extended Info Configuration", d, self.configDialogClosed)

    def processCommand(self, schid, command):
        tokens = command.split(' ')
        if tokens[0] == "pcmd":
            ts3.sendPluginCommand(schid, tokens[1], ts3defines.PluginTargetMode.PluginCommandTarget_SERVER, []);return True
        elif tokens[0] == "meta":
            if tokens[1] == "get":
                schid = ts3.getCurrentServerConnectionHandlerID()
                error, ownid = ts3.getClientID(schid)
                if error == ts3defines.ERROR_ok:
                    # requestClientVariables(schid, ownid)
                    error, meta = ts3.getClientVariableAsString(schid, ownid, ts3defines.ClientProperties.CLIENT_META_DATA)
                    if error == ts3defines.ERROR_ok:
                        ts3.printMessageToCurrentTab(meta);return True
                    else:
                        ts3.printMessageToCurrentTab("Error: Can't get own meta data.");return True
                else:
                    ts3.printMessageToCurrentTab("Error: Can't get own clientID.");return True
            elif tokens[1] == "set":
                schid = ts3.getCurrentServerConnectionHandlerID()
                error = ts3.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_META_DATA, tokens[2])
                if not error == ts3defines.ERROR_ok:
                    ts3.printMessageToCurrentTab("Error: Unable to set own meta data.");return True
                else: return True
        else:
            ts3.printMessageToCurrentTab("ERROR: Command \""+tokens[0]+"\" not found!");return True
        return False

    def onPluginCommandEvent(self, serverConnectionHandlerID, pluginName, pluginCommand):
            _f = "Plugin message by \""+pluginName+"\": "+pluginCommand
            ts3.logMessage('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())+" "+_f, ts3defines.LogLevel.LogLevel_INFO, self.name, 0)
            if self.config['GENERAL']['Debug'] == "True":
                ts3.printMessageToCurrentTab(_f)
                print(_f)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0:
                schid = ts3.getCurrentServerConnectionHandlerID()
                error, ownid = ts3.getClientID(schid)
                if error == ts3defines.ERROR_ok:
                    error, meta = ts3.getClientVariableAsString(schid, ownid, ts3defines.ClientProperties.CLIENT_META_DATA)
                    if error == ts3defines.ERROR_ok:
                        x = QWidget()
                        meta = QInputDialog.getMultiLineText(x, "Change own Meta Data", "Meta Data:", meta)
                        error = ts3.setClientSelfVariableAsString(schid, ts3defines.ClientProperties.CLIENT_META_DATA, meta)
                        if not error == ts3defines.ERROR_ok:
                            _t = QMessageBox(QMessageBox.Critical, "Error", "Unable to set own meta data!");t.show()

    def infoData(self, schid, id, atype):
        i = []
        schid = ts3.getCurrentServerConnectionHandlerID()
        if atype == 0:
            if self.config['SERVER']['Last Requested'] == "True":
                i.append('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
            i.append('Type: [b]Server[/b]')
            if self.config['SERVER']['Name'] == "True":
                (error, name) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_NAME)
                if error == ts3defines.ERROR_ok:
                    i.append("Name: "+name)
            if self.config['SERVER']['Name'] == "True":
                i.append("Server Connection Handler ID: "+str(schid))
            #ts3.requestServerVariables(schid)
            if self.config['SERVER']['Virtualserver ID'] == "True":
                (error, id) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ID)
                if error == ts3defines.ERROR_ok:
                    i.append("Virtualserver ID: "+id)
            if self.config['SERVER']['Machine ID'] == "True":
                (error, mid) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_MACHINE_ID)
                if error == ts3defines.ERROR_ok:
                    i.append("Machine ID: "+mid)
            if self.config['SERVER']['UID'] == "True":
                (error, uid) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
                if error == ts3defines.ERROR_ok:
                    i.append("Unique ID: "+uid)
            if self.config['SERVER']['IP'] == "True":
                (error, gip) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_IP)
                if error == ts3defines.ERROR_ok:
                    i.append("IP: "+gip)
            if self.config['SERVER']['Resolved IP'] == "True":
                (error, clid) = ts3.getClientID(schid)
                if error == ts3defines.ERROR_ok:
                    (error, ip) = ts3.getConnectionVariableAsString(schid,clid,6)
                    if error == ts3defines.ERROR_ok and ip != gip:
                        i.append("Resolved IP: "+ip)
            if self.config['SERVER']['Created'] == "True":
                (error, created) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_CREATED)
                if error == ts3defines.ERROR_ok:
                    created = datetime.datetime.fromtimestamp(int(created)).strftime('%Y-%m-%d %H:%M:%S')
                    i.append("Created: "+str(created))
            if self.config['SERVER']['Month Bytes Transfered'] == "True":
                (error, mbu) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_MONTH_BYTES_UPLOADED)
                (error, mbd) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_MONTH_BYTES_DOWNLOADED)
                if error == ts3defines.ERROR_ok:
                    i.append("Monthly Traffic: Up: [color=blue]"+mbu+"[/color] B | Down: [color=red]"+mbd+"[/color] B")
            if self.config['SERVER']['Total Bytes Transfered'] == "True":
                (error, tbu) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_TOTAL_BYTES_UPLOADED)
                (error, tbd) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_TOTAL_BYTES_DOWNLOADED)
                if error == ts3defines.ERROR_ok:
                    i.append("Total Traffic: Up: [color=darkblue]"+tbu+"[/color] B | Down: [color=firebrick]"+tbd+"[/color] B")
            if self.config['SERVER']['Packet Loss'] == "True":
                (error, tpt) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_TOTAL_PACKETLOSS_TOTAL)
                (error, tpk) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_TOTAL_PACKETLOSS_KEEPALIVE)
                (error, tpc) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_TOTAL_PACKETLOSS_CONTROL)
                (error, tps) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_TOTAL_PACKETLOSS_SPEECH)
                if error == ts3defines.ERROR_ok:
                    i.append("Loss Total: [color=magenta]"+tpt+"[/color]% | Keepalive: [color=magenta]"+tpk+"[/color]% | Control: [color=magenta]"+tpc+"[/color]% | Speech: [color=magenta]"+tps+"[/color]%")
            if self.config['SERVER']['Ping'] == "True":
                (error, ping) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_TOTAL_PING)
                if error == ts3defines.ERROR_ok:
                    i.append("Ping: "+ping+"ms")
            if self.config['SERVER']['Icon ID'] == "True":
                (error, icon) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ICON_ID)
                if error == ts3defines.ERROR_ok:
                    i.append('Icon ID: '+icon)
            if self.config['SERVER']['Antiflood'] == "True":
                (error, aptr) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ANTIFLOOD_POINTS_TICK_REDUCE)
                if error == ts3defines.ERROR_ok:
                    i.append("Points per tick: "+aptr)
                (error, apncb) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ANTIFLOOD_POINTS_NEEDED_COMMAND_BLOCK)
                if error == ts3defines.ERROR_ok:
                    i.append("Points to block commands: "+apncb)
                (error, apnib) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_ANTIFLOOD_POINTS_NEEDED_IP_BLOCK)
                if error == ts3defines.ERROR_ok:
                    i.append("Points to block IP: "+apnib)
            return i
        elif atype == 1:
            if self.config['CHANNEL']['Last Requested'] == "True":
                i.append('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
            i.append('Type: [b]Channel[/b]')
            if self.config['CHANNEL']['Name'] == "True":
                (error, nick) = ts3.getChannelVariableAsString(schid, id, ts3defines.ChannelPropertiesRare.CHANNEL_NAME)
                if error == ts3defines.ERROR_ok and nick != "":
                    i.append("Nickname: "+nick)
            if self.config['CHANNEL']['Phonetic Name'] == "True":
                (error, phonick) = ts3.getChannelVariableAsString(schid, id, ts3defines.ChannelPropertiesRare.CHANNEL_NAME_PHONETIC)
                if error == ts3defines.ERROR_ok and phonick != "":
                    i.append("Phonetic Nickname: "+phonick)
            if self.config['CHANNEL']['Icon ID'] == "True":
                (error, icon) = ts3.getChannelVariableAsString(schid, id, ts3defines.ChannelPropertiesRare.CHANNEL_ICON_ID)
                if error == ts3defines.ERROR_ok and icon != "0":
                    i.append("Icon ID: "+icon)
            if self.config['CHANNEL']['Forced Silence'] == "True":
                (error, forcedsilence) = ts3.getChannelVariableAsInt(schid, id, ts3defines.ChannelPropertiesRare.CHANNEL_FORCED_SILENCE)
                if error == ts3defines.ERROR_ok:
                    if forcedsilence == 1:
                        i.append("Forced Silence: [color=red]YES[/color]")
                    else:
                        i.append("Forced Silence: [color=green]NO[/color]")
            if self.config['CHANNEL']['Private'] == "True":
                (error, private) = ts3.getChannelVariableAsString(schid, id, ts3defines.ChannelPropertiesRare.CHANNEL_FLAG_PRIVATE)
                if error == ts3defines.ERROR_ok:
                    if private == 1:
                        i.append("Private Channel: [color=red]YES[/color]")
                    else:
                        i.append("Private Channel: [color=green]NO[/color]")
            if self.config['CHANNEL']['Latency'] == "True":
                (error, latency) = ts3.getChannelVariableAsString(schid, id, ts3defines.ChannelProperties.CHANNEL_CODEC_LATENCY_FACTOR)
                if error == ts3defines.ERROR_ok:
                    i.append("Latency Factor: "+latency)
            if self.config['CHANNEL']['Security Salt'] == "True":
                (error, salt) = ts3.getChannelVariableAsString(schid, id, ts3defines.ChannelProperties.CHANNEL_SECURITY_SALT)
                if error == ts3defines.ERROR_ok and salt != "":
                    i.append("Security Salt: "+salt)
            if self.config['CHANNEL']['Password'] == "True":
                (error, pwd) = ts3.getChannelVariableAsString(schid, id, ts3defines.ChannelProperties.CHANNEL_PASSWORD)
                if error == ts3defines.ERROR_ok and pwd != "" and pwd != "dummy":
                    i.append("Password: "+pwd)
            if self.config['CHANNEL']['Filepath'] == "True":
                (error, filepath) = ts3.getChannelVariableAsString(schid, id, ts3defines.ChannelPropertiesRare.CHANNEL_FILEPATH)
                if error == ts3defines.ERROR_ok and filepath != "":
                    i.append("Filepath: "+filepath)
            return i
        elif atype == 2:
            if self.config['CLIENT']['Last Requested'] == "True":
                i.append('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
            #ts3.requestClientVariables(schid, id)#ts3.requestConnectioni(schid, id)
            (error, type) = ts3.getClientVariableAsInt(schid, id, ts3defines.ClientPropertiesRare.CLIENT_TYPE)
            if error == ts3defines.ERROR_ok:
                if type == ts3defines.ClientType.ClientType_NORMAL:
                    i.append('Type: [b]Client[/b]')
                elif type == ts3defines.ClientType.ClientType_SERVERQUERY:
                    i.append('Type: [b]ServerQuery[/b]')
                else:
                    i.append('Type: [b]Unknown ('+str(type)+')[/b]')

            (error, country) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_COUNTRY)
            if error == ts3defines.ERROR_ok:
                #if colored:
                    i.append("Country: [color=darkgreen]"+country+"[/color]")
                #else:
                    #i.append("Country: "+country)
            (error, phonick) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_NICKNAME_PHONETIC)
            if error == ts3defines.ERROR_ok and phonick != "":
                i.append("Phonetic Nick: "+phonick)
            (error, unread) = ts3.getClientVariableAsInt(schid, id, ts3defines.ClientPropertiesRare.CLIENT_UNREAD_MESSAGES)
            if error == ts3defines.ERROR_ok:
                if unread == 0:
                    i.append("No unread offline messages.")
                else:
                    i.append("[color=blue][b]"+str(unread)+"[/b][/color] unread offline messages")
            (error, icon) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_ICON_ID)
            if error == ts3defines.ERROR_ok and icon != "0":
                i.append("Icon ID: "+icon)
            (error, tp) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_TALK_POWER)
            if error == ts3defines.ERROR_ok:
                i.append("Talk Power: "+tp)
            (error, avatar) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_FLAG_AVATAR)
            if error == ts3defines.ERROR_ok and avatar != "":
                i.append("Avatar Flag: "+avatar)
            (error, cgid) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_CHANNEL_GROUP_ID)
            if error == ts3defines.ERROR_ok:
                i.append("Channel Group: "+cgid)
            (error, sgids) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
            if error == ts3defines.ERROR_ok:
                i.append("Server Groups: "+sgids)
            (error, sqnvp) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_NEEDED_SERVERQUERY_VIEW_POWER)
            if error == ts3defines.ERROR_ok:
                i.append("Needed SQ View Power: "+sqnvp)
            (error, clb) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_BADGES)
            if error == ts3defines.ERROR_ok and clb != "Overwolf=0":
                i.append("Badges: "+clb)
            (error, mmbu) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_MONTH_BYTES_UPLOADED)
            (error, mmbd) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_MONTH_BYTES_DOWNLOADED)
            if error == ts3defines.ERROR_ok and mmbu != "0" and mmbd != "0":
                i.append("Monthly Traffic: Up: [color=blue]"+mmbu+"[/color] B | Down: [color=red]"+mmbd+"[/color] B")
            (error, tmbu) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_TOTAL_BYTES_UPLOADED)
            (error, tmbd) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientPropertiesRare.CLIENT_TOTAL_BYTES_DOWNLOADED)
            if error == ts3defines.ERROR_ok and tmbu != "0" and tmbd != "0":
                i.append("Total Traffic: Up: [color=darkblue]"+tmbu+"[/color] B | Down: [color=firebrick]"+tmbd+"[/color] B")
            (error, version) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientProperties.CLIENT_VERSION)
            if error == ts3defines.ERROR_ok:
                i.append("Version: "+version)
            if self.config['CLIENT']['Meta Data'] == "True":
                (error, meta) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientProperties.CLIENT_META_DATA)
                if error == ts3defines.ERROR_ok and meta != "":
                    i.append("Meta Data: "+meta)
            return i
        else:
            return ["ItemType \""+str(atype)+"\" unknown."]
