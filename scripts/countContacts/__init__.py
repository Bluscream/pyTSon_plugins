from ts3plugin import ts3plugin
from bluscream import *
from pytson import getCurrentApiVersion
import ts3defines, ts3lib, ts3client

class countContacts(ts3plugin):
    name = "Count Contacts"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = True
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
        db = ts3client.Config()
        q = db.query("SELECT * FROM contacts")
        while q.next():
            for line in q.value("value").split('\n'):
                if line.startswith('Friend='):
                    status = int(line[-1])
                    if status == ContactStatus.FRIEND: buddies += 1
                    elif status == ContactStatus.BLOCKED: blocked += 1
                    elif status == ContactStatus.NEUTRAL: neutral += 1
                    else: unknown += 1
                elif line.lower().startswith('nickname=w/'):
                    female += 1
                elif line.lower().startswith('nickname=m/'):
                    male += 1
        del db
        sum = buddies+blocked+neutral+unknown
        msg = ["Contacts: [b]{}[/b]".format(sum)]
        msg.append("[color=green]Buddies[/color]: [b]{}[/b] ({}%)".format(buddies, percentage(buddies, sum)))
        msg.append("[color=red]Blocked[/color]: [b]{}[/b] ({}%)".format(blocked, percentage(blocked, sum)))
        msg.append("Neutral: [b]{}[/b] ({}%)".format(neutral, percentage(neutral, sum)))# [color=white][/color]
        if unknown > 0: msg.append("Unknown: [color=orange]{}[/color] ({}%)".format(unknown, percentage(unknown, sum)))
        if female > 0: msg.append("[color=purple]Female[/color]: {} ({}%)".format(female, percentage(female, sum)))
        if male > 0: msg.append("[color=lightblue]Male[/color]: {} ({}%)".format(male, percentage(male, sum)))
        return " | ".join(msg)

    def infoData(self, schid, id, atype):
        if self.count < 3: self.count += 1; return None
        clist = list()
        if atype == ts3defines.PluginItemType.PLUGIN_SERVER:
            (err, clist) = ts3lib.getClientList(schid)
        elif atype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
            return None
            (err, clist) = ts3lib.getChannelClientList(schid, id)
        else: return None
        buddies = 0;blocked = 0;neutral = 0;unknown = 0
        uidlist = []
        for clid in clist:
            (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            uidlist.append(uid)
        db = ts3client.Config()
        q = db.query("SELECT * FROM contacts")
        while q.next():
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
        _return.append("Online: {}".format(buddies+blocked+neutral+unknown))
        _return.append("Buddies: [color=green]{}[/color]".format(buddies))
        _return.append("Blocked: [color=red]{}[/color]".format(blocked))
        _return.append("Neutral: {}".format(neutral))
        if unknown > 0: _return.append("Unknown: [color=orange]{}[/color]".format(unknown))
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