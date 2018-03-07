from ts3plugin import ts3plugin, PluginHost
from bluscream import *
from configparser import ConfigParser
from getvalues import getValues, ValueType
from pytson import getPluginPath, getCurrentApiVersion
from PythonQt.QtGui import QDialog
import ts3defines, ts3lib, ts3client, time

class countContacts(ts3plugin):
    name = "Count Contacts"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1"
    author = "Bluscream"
    description = "Gives you numbers"
    offersConfigure = True
    commandKeyword = "ccount"
    infoTitle = "[b]Contacts:[/b]"
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, name, ""),
                 (ts3defines.PluginItemType.PLUGIN_CHANNEL, 0, "Send Contact Stats", ""),
                 (ts3defines.PluginItemType.PLUGIN_CLIENT, 0, "Send Contact Stats", "")
                ]
    hotkeys = []
    count = 0
    ini = os.path.join(getPluginPath(), "scripts", "countContacts", "settings.ini")
    config = ConfigParser()

    def __init__(self):
        if os.path.isfile(self.ini): self.config.read(self.ini)
        else:
            self.config['general'] = { "Male Prefix": "m/", "Female Prefix": "f/", "Soundboard Prefix": "s/" }
            with open(self.ini, 'w') as configfile: self.config.write(configfile)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def configure(self, qParentWidget):
        d = dict()
        d['Male Prefix'] = (ValueType.string, "Male", self.config['general']['Male Prefix'], None, 1)
        d['Female Prefix'] = (ValueType.string, "Female", self.config['general']['Female Prefix'], None, 1)
        d['Soundboard Prefix'] = (ValueType.string, "Soundboard", self.config['general']['Soundboard Prefix'], None, 1)
        getValues(None, "Count Contacts Prefixes", d, self.configDialogClosed)

    def configDialogClosed(self, r, vals):
        if r != QDialog.Rejected:
            self.config["general"] = {
                "Male Prefix": str(vals["Male Prefix"]),
                "Female Prefix": str(vals["Female Prefix"]),
                "Soundboard Prefix": str(vals["Soundboard Prefix"])
            }
            with open(self.ini, 'w') as configfile:
                self.config.write(configfile)

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
        female = 0;male = 0;soundboard = 0
        f_buddies = 0;m_buddies = 0
        f_blocked = 0;m_blocked = 0
        f_neutral = 0;m_neutral = 0
        f_unknown = 0;m_unknown = 0
        contacts = getContacts()
        contact = None
        first = round(time.time()); last = 0
        firstc = None; lastc = None
        for contact in contacts:
            nick = contact["Nickname"].decode("utf-8").lower()
            if nick.startswith(self.config['general']['Female Prefix']): female += 1
            elif nick.startswith(self.config['general']['Male Prefix']): male += 1
            elif nick.startswith(self.config['general']['Soundboard Prefix']): soundboard += 1
            status = contact["Friend"]
            if status == ContactStatus.FRIEND:
                buddies += 1
                if nick.startswith(self.config['general']['Female Prefix']): f_buddies += 1
                elif nick.startswith(self.config['general']['Male Prefix']): m_buddies += 1
            elif status == ContactStatus.BLOCKED:
                blocked += 1
                if nick.startswith(self.config['general']['Female Prefix']): f_blocked += 1
                elif nick.startswith(self.config['general']['Male Prefix']): m_blocked += 1
            elif status == ContactStatus.NEUTRAL:
                neutral += 1
                if nick.startswith(self.config['general']['Female Prefix']): f_neutral += 1
                elif nick.startswith(self.config['general']['Male Prefix']): m_neutral += 1
            else:
                unknown += 1
                if nick.startswith(self.config['general']['Female Prefix']): f_unknown += 1
                elif nick.startswith(self.config['general']['Male Prefix']): m_unknown += 1
            if "LastSeenEpoch" in contact:
                if contact["LastSeenEpoch"] < first:
                    first = contact["LastSeenEpoch"]
                    firstc = contact
                if contact["LastSeenEpoch"] > last:
                    last = contact["LastSeenEpoch"]
                    lastc = contact
        sum = buddies+blocked+neutral+unknown
        msg = ["My Contact Stats:"]
        msg.append("Sum: [b]{}[/b] | [color=purple]Female[/color]: {} ({}%) | [color=lightblue]Male[/color]: {} ({}%) | Others: {} ({}%){}".format(
                    sum, female, percentage(female, sum), male, percentage(male, sum), sum-(male+female), percentage(sum-(male+female), sum), " | Soundboard: {} ({}%)".format(soundboard, percentage(soundboard, sum)) if soundboard > 0 else ""))
        msg.append("[color=green]Buddies[/color]: [b]{}[/b] ({}%) | [color=purple]Female[/color]: {} ({}%) | [color=lightblue]Male[/color]: {} ({}%) | Others: {} ({}%)".format(
                    buddies, percentage(buddies, sum), f_buddies, percentage(f_buddies, buddies), m_buddies, percentage(m_buddies, buddies), buddies-(m_buddies+f_buddies), percentage(buddies-(m_buddies+f_buddies), buddies)))
        msg.append("[color=red]Blocked[/color]: [b]{}[/b] ({}%) | [color=purple]Female[/color]: {} ({}%) | [color=lightblue]Male[/color]: {} ({}%) | Others: {} ({}%)".format(
                    blocked, percentage(blocked, sum), f_blocked, percentage(f_blocked, blocked), m_blocked, percentage(m_blocked, blocked), blocked-(m_blocked+f_blocked), percentage(blocked-(m_blocked+f_blocked), blocked)))
        msg.append("Neutral: [b]{}[/b] ({}%) | [color=purple]Female[/color]: {} ({}%) | [color=lightblue]Male[/color]: {} ({}%) | Others: {} ({}%)".format(
                    neutral, percentage(neutral, sum), f_neutral, percentage(f_neutral, neutral), m_neutral, percentage(m_neutral, neutral), neutral-(m_neutral+f_neutral), percentage(neutral-(m_neutral+f_neutral), neutral)))
        if unknown > 0: msg.append("Unknown: [color=orange]{}[/color] ({}%) | [color=purple]Female[/color]: {} ({}%) | [color=lightblue]Male[/color]: {} ({}%) | Others: {} ({}%)".format(
                    unknown, percentage(unknown, sum), f_unknown, percentage(f_unknown, unknown), m_unknown, percentage(m_unknown, unknown), unknown-(m_unknown+f_unknown), percentage(unknown-(m_unknown+f_unknown), unknown)))
        if first:
            msg.append("First: {} {} {} on {}".format(
            firstc["LastSeen"].replace("T", " "), self.readableContactStatus(firstc), clientURL(1, 0, firstc["IDS"], firstc["Nickname"].decode("utf-8", "ignore")), channelURL(1, 0, firstc["LastSeenServerName"].decode("utf-8", "ignore"))))
        if last:
            msg.append("Last: {} {} {} on {}".format(
            lastc["LastSeen"].replace("T", " "), self.readableContactStatus(firstc), clientURL(1, 0, lastc["IDS"], lastc["Nickname"].decode("utf-8", "ignore")), channelURL(1, 0, lastc["LastSeenServerName"].decode("utf-8", "ignore"))))
        return "\n".join(msg)

    def readableContactStatus(self, contact):
        if contact["Friend"] == 0: return "[color=green]Friend[/color]"
        elif contact["Friend"] == 1: return "[color=red]Blocked[/color]"
        elif contact["Friend"] == 2: return "Neutral"
        else: return "[color=orange]Unknown[/color]"

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