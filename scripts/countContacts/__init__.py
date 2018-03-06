from ts3plugin import ts3plugin, PluginHost
from bluscream import *
from pytson import getCurrentApiVersion
import ts3defines, ts3lib, ts3client, time

def getContacts():
    db = ts3client.Config()
    ret = []
    q = db.query("SELECT * FROM contacts")
    while q.next():
        try:
            key = int(q.value("key"))
            cur[key] = {"Timestamp": q.value("timestamp")}
            val = q.value("value")
            for l in val.split('\n'):
                try:
                    l = l.split('=', 1)
                    if l[0] in ["Nickname", "LastSeenServerName"]: ret[key][l[0]] = u"".format(l[1])
                    else:
                        try: ret[key][l[0]] = int(l[1])
                        except: ret[key][l[0]] = l[1]
                    if l[0] == "LastSeen" and l[1]: ret[key]["LastSeenEpoch"] = int(time.mktime(time.strptime(l[1], '%Y-%m-%dT%H:%M:%S')))
                except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0);continue
            """
            for k, v in ret[key].items():
                print("key:", k, "val:", v)
            """
        except: from traceback import format_exc;ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0);continue
    del db
    return ret

class countContacts(ts3plugin):
    name = "Count Contacts"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1"
    author = "Bluscream"
    description = "Gives you numbers"
    offersConfigure = False
    commandKeyword = "ccount"
    infoTitle = "[b]Contacts:[/b]"
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, ""),
                 (ts3defines.PluginItemType.PLUGIN_CHANNEL, 0, "Send Contact Stats", ""),
                 (ts3defines.PluginItemType.PLUGIN_CLIENT, 0, "Send Contact Stats", "")
                ]
    hotkeys = []
    count = 0

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID != 0: return
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            self.printContacts()
        elif atype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
            ts3lib.requestSendChannelTextMsg(schid, self.contactStats(), selectedItemID)
        elif atype == ts3defines.PluginItemType.PLUGIN_CLIENT:
            ts3lib.requestSendPrivateTextMsg(schid, self.contactStats(), selectedItemID)

    def processCommand(self, schid, command): self.printContacts(); return True

    def printContacts(self):
        ts3lib.printMessageToCurrentTab("{}{}".format(timestamp(), self.contactStats()))

    def contactStats(self):
        buddies = 0;blocked = 0;neutral = 0;unknown = 0
        female = 0;male = 0
        f_buddies = 0;m_buddies = 0;
        f_blocked = 0;m_blocked = 0;
        f_neutral = 0;m_neutral = 0;
        f_unknown = 0;m_unknown = 0;
        contacts = getContacts()
        contact = None
        times = []
        for contact in contacts:
            print("current contact:", contact)
            nick = contact["Nickname"].lower()
            if nick.startswith('w/'): female += 1
            elif nick.startswith('m/'): male += 1
            status = contact["Friend"]
            if status == ContactStatus.FRIEND:
                buddies += 1
                if nick.startswith('w/'): f_buddies += 1
                elif nick.startswith('m/'): m_buddies += 1
            elif status == ContactStatus.BLOCKED:
                blocked += 1
                if nick.startswith('w/'): f_blocked += 1
                elif nick.startswith('m/'): m_blocked += 1
            elif status == ContactStatus.NEUTRAL:
                neutral += 1
                if nick.startswith('w/'): f_neutral += 1
                elif nick.startswith('m/'): m_neutral += 1
            else:
                unknown += 1
                if nick.startswith('w/'): f_unknown += 1
                elif nick.startswith('m/'): m_unknown += 1
            if hasattr(contact, "LastSeenEpoch"): times.append(contact["LastSeenEpoch"])
        sum = buddies+blocked+neutral+unknown
        msg = ["My Contact Stats:"]
        msg.append("Sum: [b]{}[/b] | [color=purple]Female[/color]: {} ({}%) | [color=lightblue]Male[/color]: {} ({}%) | Others: {} ({}%)".format(
                    sum, female, percentage(female, sum), male, percentage(male, sum), sum-(male+female), percentage(sum-(male+female), sum)))
        msg.append("[color=green]Buddies[/color]: [b]{}[/b] ({}%) | [color=purple]Female[/color]: {} ({}%) | [color=lightblue]Male[/color]: {} ({}%) | Others: {} ({}%)".format(
                    buddies, percentage(buddies, sum), f_buddies, percentage(f_buddies, buddies), m_buddies, percentage(m_buddies, buddies), buddies-(m_buddies+f_buddies), percentage(buddies-(m_buddies+f_buddies), buddies)))
        msg.append("[color=red]Blocked[/color]: [b]{}[/b] ({}%) | [color=purple]Female[/color]: {} ({}%) | [color=lightblue]Male[/color]: {} ({}%) | Others: {} ({}%)".format(
                    blocked, percentage(blocked, sum), f_blocked, percentage(f_blocked, blocked), m_blocked, percentage(m_blocked, blocked), blocked-(m_blocked+f_blocked), percentage(blocked-(m_blocked+f_blocked), blocked)))
        msg.append("Neutral: [b]{}[/b] ({}%) | [color=purple]Female[/color]: {} ({}%) | [color=lightblue]Male[/color]: {} ({}%) | Others: {} ({}%)".format(
                    neutral, percentage(neutral, sum), f_neutral, percentage(f_neutral, neutral), m_neutral, percentage(m_neutral, neutral), neutral-(m_neutral+f_neutral), percentage(neutral-(m_neutral+f_neutral), neutral)))
        if unknown > 0: msg.append("Unknown: [color=orange]{}[/color] ({}%) | [color=purple]Female[/color]: {} ({}%) | [color=lightblue]Male[/color]: {} ({}%) | Others: {} ({}%)".format(
                    unknown, percentage(unknown, sum), f_unknown, percentage(f_unknown, unknown), m_unknown, percentage(m_unknown, unknown), unknown-(m_unknown+f_unknown), percentage(unknown-(m_unknown+f_unknown), unknown)))
        # msg.append("First: {} ({}) | Last: {} ({})".format(contacts[0]["Nickname"], contacts[0]["LastSeen"], contacts[sorted(contacts.keys())[-1]]["Nickname"], contacts[sorted(contacts.keys())[-1]]["LastSeen"]))
        # if female > 0: msg.append("[color=purple]Female[/color]: {} ({}%)".format(female, percentage(female, sum)))
        # if male > 0: msg.append("[color=lightblue]Male[/color]: {} ({}%)".format(male, percentage(male, sum)))
        return "\n".join(msg)

    def infoData(self, schid, id, atype):
        if self.count < 3: self.count += 1; return None
        clist = list()
        if atype == ts3defines.PluginItemType.PLUGIN_SERVER:
            (err, clist) = ts3lib.getClientList(schid)
        elif atype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
            return None
            (err, clist) = ts3lib.getChannelClientList(schid, id)
        else: return None
        sum = 0;buddies = 0;blocked = 0;neutral = 0;unknown = 0
        uidlist = []
        for clid in clist:
            (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            uidlist.append(uid)
        db = ts3client.Config()
        q = db.query("SELECT * FROM contacts")
        while q.next():
            sum += 1
            val = q.value("value").split('\n')
            uid = ""
            for line in val:
                if line.startswith('IDS='):
                    uid = line.split('IDS=')[1]
            if not uid in uidlist: continue
            for line in val:
                if line.startswith('Friend='):
                    status = int(line[-1])
                    if status == ContactStatus.FRIEND: buddies += 1
                    elif status == ContactStatus.BLOCKED: blocked += 1
                    elif status == ContactStatus.NEUTRAL: neutral += 1
                    else: unknown += 1
        del db
        _return = list()
        _sum = buddies+blocked+neutral+unknown
        _return.append("Online: {} / {} ({}%)".format(_sum, sum, percentage(_sum, sum)))
        _return.append("[color=green]Buddies[/color]: {} ({}%)".format(buddies, percentage(buddies, _sum)))
        _return.append("[color=red]Blocked[/color]: {} ({}%)".format(blocked, percentage(blocked, _sum)))
        _return.append("Neutral: {} ({}%)".format(neutral, percentage(neutral, _sum)))
        if unknown > 0: _return.append("[color=orange]Unknown[/color]: {} ({}%)".format(unknown, percentage(unknown, _sum)))
        return _return


"""
Nickname=w/Tina Apokalypse
Friend=0
Automute=false
IgnorePublicMessages=false
IgnorePrivateMessages=false
IgnorePokes=false
IgnoreAvatar=false
IgnoreAwayMessage=false
NickShowType=2
HaveVolumeModifier=true
VolumeModifier=0
WhisperAllow=true
PhoneticNickname=
LastSeen=2017-11-29T22:20:03
LastSeenServerName=VIP CLAN
LastSeenServerAddress=
IDS=MLxQx2MkV48xigapaMiKkCXyOZQ=
"""