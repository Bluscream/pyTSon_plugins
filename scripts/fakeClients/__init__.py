from ts3plugin import ts3plugin, PluginHost
from random import choice, getrandbits, randint
from bluscream import timestamp, sendCommand, calculateInterval, AntiFloodPoints, varname, random_string
from traceback import format_exc
import ts3defines, ts3lib

class fakeClients(ts3plugin):
    name = "Fake Clients"
    apiVersion = 21
    requestAutoload = False
    version = "1"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "fc"
    infoTitle = None
    menuItems = []
    hotkeys = []
    clients = {}

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def processCommand(self, schid, command):
        clients = 1
        try: clients = int(command)
        except: pass
        for i in range(clients):
            cmd = "notifycliententerview"
            client = self.fakeClient(schid)
            for k in client:
                if client[k] != "":
                    cmd += " {}={}".format(k, client[k])
                else: cmd += " {}".format(k)
            sendCommand(self.name, cmd, schid, True, "-")
            # self.clients.append(client["clid"])
        return True

    def fakeClient(self, schid):
        client = {}
        client["reasonid"] = "0"
        client["cfid"] = "0"
        (err, cids) = ts3lib.getChannelList(schid)
        cid = choice(cids)
        # (err, clid) = ts3lib.getClientID(schid)
        # (err, cid) = ts3lib.getChannelOfClient(schid, clid)
        client["ctid"] = cid
        e, client["client_channel_group_id"] = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_CHANNEL_GROUP)
        e, client["client_servergroups"] = ts3lib.getServerVariable(schid, ts3defines.VirtualServerPropertiesRare.VIRTUALSERVER_DEFAULT_SERVER_GROUP)
        client["client_channel_group_inherited_channel_id"] = cid # Does it work?
        client["client_input_muted"] = randint(0,1)
        client["client_output_muted"] = randint(0,1)
        client["client_outputonly_muted"] = randint(0,1)
        client["client_input_hardware"] = randint(0,1)
        client["client_output_hardware"] = randint(0,1)
        client["client_is_recording"] = randint(0,1)
        client["client_talk_request"] = randint(0,1)
        client["client_type"] = randint(0,1)
        client["client_is_talker"] = randint(0,1)
        client["client_away"] = randint(0,1)
        client["client_is_channel_commander"] = randint(0,1)
        client["client_is_priority_speaker"] = randint(0,1)
        client["clid"] = randint(0,100)
        client["client_database_id"] = randint(0,1000)
        client["client_talk_power"] = randint(0,99999)
        client["client_unread_messages"] = randint(0,65000)
        client["client_needed_serverquery_view_power"] = 0 # randint(0,65000)
        client["client_icon_id"] = randint(0,65000)
        client["client_unique_identifier"] = "{}=".format(random_string(27))
        client["client_nickname"] = random_string(randint(3,30))
        client["client_meta_data"] = random_string(randint(0,10)) # 30
        client["client_away_message"] = random_string(randint(0,10)) # 80
        client["client_flag_avatar"] = random_string(32)
        client["client_talk_request_msg"] = random_string(randint(0,50))
        client["client_description"] = random_string(randint(0,50))
        client["client_nickname_phonetic"] = random_string(randint(3,30))
        client["client_country"] = "DE" # random_string(2).upper()
        client["client_badges"] = random_string(randint(0,30))
        return client