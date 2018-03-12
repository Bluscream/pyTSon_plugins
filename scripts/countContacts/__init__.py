from ts3plugin import ts3plugin, PluginHost
from bluscream import *
from configparser import ConfigParser
from getvalues import getValues, ValueType
from pytsonui import setupUi
from pytson import getPluginPath, getCurrentApiVersion
from PythonQt.QtGui import QDialog, QTableWidgetItem, QComboBox, QCheckBox
from PythonQt.QtCore import Qt
from traceback import format_exc
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
                 (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Online Contacts", ""),
                 (ts3defines.PluginItemType.PLUGIN_CHANNEL, 0, "Send Contact Stats", ""),
                 (ts3defines.PluginItemType.PLUGIN_CLIENT, 0, "Send Contact Stats", "")]
    hotkeys = []
    count = 0
    ini = os.path.join(getPluginPath(), "scripts", "countContacts", "settings.ini")
    ui = os.path.join(getPluginPath(), "scripts", "countContacts", "filters.ui")
    cfg = ConfigParser()
    cfg.optionxform=str
    dlg = None

    def __init__(self):
        if os.path.isfile(self.ini): self.cfg.read(self.ini)
        else:
            self.cfg['filters'] = { "Male": "m/", "Female": "f/" }
            with open(self.ini, 'w') as configfile: self.cfg.write(configfile)
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def configure(self, qParentWidget):
        if not self.dlg: self.dlg = contactStatsFilters(self)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
        return QDialog.Rejected
        d = dict()
        for k in self.cfg['filters']:
            d[k] = (ValueType.string, k, self.cfg['filters'][k], None, 1)
        getValues(None, "Count Contacts Prefixes", d, self.configDialogClosed)

    def configDialogClosed(self, r, vals):
        if r == QDialog.Rejected: return
        for val in vals:
            self.cfg.set("general", val, vals[val])
        with open(self.ini, 'w') as configfile:
            self.cfg.write(configfile)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0: self.printContacts()
            elif menuItemID == 1: ts3lib.printMessageToCurrentTab("{}{}".format(timestamp(), self.onlineContacts(schid, False)))
        elif atype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
            ts3lib.requestSendChannelTextMsg(schid, self.contactStats(), selectedItemID)
        elif atype == ts3defines.PluginItemType.PLUGIN_CLIENT:
            ts3lib.requestSendPrivateTextMsg(schid, self.contactStats(), selectedItemID)

    def processCommand(self, schid, command): self.printContacts(); return True

    def printContacts(self):
        ts3lib.printMessageToCurrentTab("{}{}".format(timestamp(), self.contactStats(True)))

    def checkFilters(self, counters, nick):
        for k in self.cfg['filters']:
            tmp = self.cfg.get('filters', k).split('|', 2)
            case = bool(int(tmp[0]));mode = tmp[1];text = tmp[2]
            if case: nick = nick.lower(); text = text.lower()
            if mode == "Prefix":
                if nick.startswith(text): counters[k] += 1
            elif mode == "Suffix":
                if nick.endswith(text): counters[k] += 1
            elif mode == "Contains":
                if text in nick: counters[k] += 1
            elif mode == "Equals":
                if text == nick: counters[k] += 1

    def onlineContacts(self, schid, neutral=list()):
        contacts = getContacts()
        lst = {}
        for contact in contacts:
            lst[contact["IDS"]] = contact["Friend"]
        del contacts
        (err, clist) = ts3lib.getClientList(schid)
        buddies = [];blocked = [];unknown = []
        for clid in clist:
            (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            if not uid in lst: continue
            if lst[uid] == ContactStatus.FRIEND: buddies.append(clientURL(schid, clid, uid))
            elif lst[uid] == ContactStatus.BLOCKED: blocked.append(clientURL(schid, clid, uid))
            elif lst[uid] == ContactStatus.NEUTRAL:
                if neutral: neutral.append(clientURL(schid, clid, uid))
            else: unknown.append(clientURL(schid, clid, uid))
        _sum = len(buddies)+len(blocked)+len(unknown)
        if neutral: _sum += len(neutral)
        msg = ["[u]My Online Contacts [/u]: [b]{}[/b]".format(_sum)]
        if len(buddies) > 0: msg.append("[b]{}[/b] [color=green]Buddies[/color]: {}".format(len(buddies), " | ".join(buddies)))
        if len(blocked) > 0: msg.append("[b]{}[/b] [color=red]Blocked[/color]: {}".format(len(blocked), " | ".join(blocked)))
        if neutral and len(neutral) > 0: msg.append("[b]{}[/b] Neutral: {}".format(len(neutral), " | ".join(neutral)))
        if len(unknown) > 0: msg.append("[b]{}[/b] [color=orange]Unknown[/color]: {}".format(len(unknown), " | ".join(unknown)))
        return "\n".join(msg)

    def contactStats(self,detailed=False):
        buddies = 0;blocked = 0;neutral = 0;unknown = 0
        counters = {};bcounters = {};blcounters = {};ncounters = {}; ucounters = {}
        for k in self.cfg['filters']:
            counters[k] = 0;bcounters[k] = 0;blcounters[k] = 0;ncounters[k] = 0;ucounters[k] = 0
        contacts = getContacts()
        if detailed:
            first = round(time.time()); last = 0
            firstc = None; lastc = None
        for contact in contacts:
            nick = contact["Nickname"].decode("utf-8")
            for k in self.cfg['filters']:
                tmp = self.cfg.get('filters', k).split('|', 2)
                case = bool(int(tmp[0]));mode = tmp[1];text = tmp[2]
                if case: nick = nick.lower(); text = text.lower()
                if mode == "Prefix":
                    if nick.startswith(text): counters[k] += 1
                elif mode == "Suffix":
                    if nick.endswith(text): counters[k] += 1
                elif mode == "Contains":
                    if text in nick: counters[k] += 1
                elif mode == "Equals":
                    if text == nick: counters[k] += 1
            status = contact["Friend"]
            if status == ContactStatus.FRIEND:
                buddies += 1
                for k in self.cfg['filters']:
                    tmp = self.cfg.get('filters', k).split('|', 2)
                    case = bool(int(tmp[0]));mode = tmp[1];text = tmp[2]
                    if case: nick = nick.lower(); text = text.lower()
                    if mode == "Prefix":
                        if nick.startswith(text): bcounters[k] += 1
                    elif mode == "Suffix":
                        if nick.endswith(text): bcounters[k] += 1
                    elif mode == "Contains":
                        if text in nick: bcounters[k] += 1
                    elif mode == "Equals":
                        if text == nick: bcounters[k] += 1
            elif status == ContactStatus.BLOCKED:
                blocked += 1
                for k in self.cfg['filters']:
                    tmp = self.cfg.get('filters', k).split('|', 2)
                    case = bool(int(tmp[0]));mode = tmp[1];text = tmp[2]
                    if case: nick = nick.lower(); text = text.lower()
                    if mode == "Prefix":
                        if nick.startswith(text): blcounters[k] += 1
                    elif mode == "Suffix":
                        if nick.endswith(text): blcounters[k] += 1
                    elif mode == "Contains":
                        if text in nick: blcounters[k] += 1
                    elif mode == "Equals":
                        if text == nick: blcounters[k] += 1
            elif status == ContactStatus.NEUTRAL:
                neutral += 1
                for k in self.cfg['filters']:
                    tmp = self.cfg.get('filters', k).split('|', 2)
                    case = bool(int(tmp[0]));mode = tmp[1];text = tmp[2]
                    if case: nick = nick.lower(); text = text.lower()
                    if mode == "Prefix":
                        if nick.startswith(text): ncounters[k] += 1
                    elif mode == "Suffix":
                        if nick.endswith(text): ncounters[k] += 1
                    elif mode == "Contains":
                        if text in nick: ncounters[k] += 1
                    elif mode == "Equals":
                        if text == nick: ncounters[k] += 1
            else:
                unknown += 1
                for k in self.cfg['filters']:
                    tmp = self.cfg.get('filters', k).split('|', 2)
                    case = bool(int(tmp[0]));mode = tmp[1];text = tmp[2]
                    if case: nick = nick.lower(); text = text.lower()
                    if mode == "Prefix":
                        if nick.startswith(text): ucounters[k] += 1
                    elif mode == "Suffix":
                        if nick.endswith(text): ucounters[k] += 1
                    elif mode == "Contains":
                        if text in nick: ucounters[k] += 1
                    elif mode == "Equals":
                        if text == nick: ucounters[k] += 1
            if "LastSeenEpoch" in contact and detailed:
                if contact["LastSeenEpoch"] < first:
                    first = contact["LastSeenEpoch"]
                    firstc = contact
                if contact["LastSeenEpoch"] > last:
                    last = contact["LastSeenEpoch"]
                    lastc = contact
        sum = buddies+blocked+neutral+unknown
        msg = ["[u]My Contact Stats[/u]:"]
        tmp = []
        for c in counters: tmp.append("{}: {} ({}%)".format(c.title(), counters[c], percentage(counters[c], sum)))
        msg.append("Sum: [b]{}[/b] {}".format(sum, " | ".join(tmp)))
        if buddies > 0:
            tmp = []
            for c in bcounters: tmp.append("{}: {} ({}%)".format(c.title(), bcounters[c], percentage(bcounters[c], sum)))
            msg.append("[color=green]Buddies[/color]: [b]{}[/b] ({}%) {}".format(buddies, percentage(buddies, sum), " | ".join(tmp)))
        if blocked > 0:
            tmp = []
            for c in blcounters: tmp.append("{}: {} ({}%)".format(c.title(), blcounters[c], percentage(blcounters[c], sum)))
            msg.append("[color=red]Blocked[/color]: [b]{}[/b] ({}%) {}".format(blocked, percentage(blocked, sum), " | ".join(tmp)))
        if neutral > 0:
            tmp = []
            for c in ncounters: tmp.append("{}: {} ({}%)".format(c.title(), ncounters[c], percentage(ncounters[c], sum)))
            msg.append("Neutral: [b]{}[/b] ({}%) {}".format(neutral, percentage(neutral, sum), " | ".join(tmp)))
        if unknown > 0:
            tmp = []
            for c in ucounters: tmp.append("{}: {} ({}%)".format(c.title(), ucounters[c], percentage(ucounters[c], sum)))
            msg.append("[color=orange]Unknown[/color]: [b]{}[/b] ({}%) {}".format(unknown, percentage(unknown, sum), " | ".join(tmp)))
        if detailed and first:
            msg.append("First: {} {} {} on {}".format(
            firstc["LastSeen"].replace("T", " "), self.readableContactStatus(firstc), clientURL(1, 0, firstc["IDS"], firstc["Nickname"].decode("utf-8", "ignore")), channelURL(1, 0, firstc["LastSeenServerName"].decode("utf-8", "ignore"))))
        if detailed and last:
            msg.append("Last: {} {} {} on {}".format(
            lastc["LastSeen"].replace("T", " "), self.readableContactStatus(firstc), clientURL(1, 0, lastc["IDS"], lastc["Nickname"].decode("utf-8", "ignore")), channelURL(1, 0, lastc["LastSeenServerName"].decode("utf-8", "ignore"))))
        return "\n".join(msg)

    def readableContactStatus(self, contact):
        if contact["Friend"] == ContactStatus.FRIEND: return "[color=green]Friend[/color]"
        elif contact["Friend"] == ContactStatus.BLOCKED: return "[color=red]Blocked[/color]"
        elif contact["Friend"] == ContactStatus.NEUTRAL: return "Neutral"
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


class contactStatsFilters(QDialog):
    listen = False
    def __init__(self, script, parent=None):
        try:
            super(QDialog, self).__init__(parent)
            setupUi(self, script.ui)
            self.cfg = script.cfg
            self.ini = script.ini
            self.reloadPlugin = script.__init__
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Count Contacts Filters")
            self.setupTable()
            self.listen = True
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def setupTable(self):
        try:
            self.tbl_filters.clearContents()
            self.tbl_filters.setRowCount(0)
            for o in self.cfg.options('filters'):
                pos = self.tbl_filters.rowCount
                self.tbl_filters.insertRow(pos)
                tmp = self.cfg.get('filters', o).split('|', 2)
                chk_case = QCheckBox()
                chk_case.setChecked(bool(int(tmp[0])))
                self.tbl_filters.setCellWidget(pos, 0, chk_case)
                box_type = QComboBox()
                box_type.addItems(["Prefix", "Suffix", "Contains", "Equals"])
                box_type.connect("currentIndexChanged(int)", self.currentIndexChanged)
                box_type.setCurrentText(tmp[1])
                self.tbl_filters.setCellWidget(pos, 1, box_type)
                self.tbl_filters.setItem(pos, 2, QTableWidgetItem(o))
                self.tbl_filters.setItem(pos, 3, QTableWidgetItem(tmp[2]))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def currentIndexChanged(self, i):
        if PluginHost.cfg.getboolean("filters", "verbose"): print("test", i)
        row = self.tbl_filters.currentRow()
        if PluginHost.cfg.getboolean("filters", "verbose"): print("row:", row)
        # item = self.tbl_members.itemAt(const QPoint &point)
        # item = self.tbl_members.selectedItems()
        # print("item:", item)
        # self.tbl_members.at
        # ts3lib.requestSetClientChannelGroup(self.schid, [item.itemData], [self.channel], [self.dbid])

    def on_btn_apply_clicked(self):
        items = []
        for i in range(self.tbl_filters.rowCount):
             uid = self.lst_active.item(i)
             items.append(uid)
        self.grp_active.setTitle("{} Active".format(self.lst_active.count))
        self.cfg.set('general', 'badges', ','.join(items))
        self.setCustomBadges()

    def on_btn_save_clicked(self):
        with open(self.ini, 'w') as configfile: self.cfg.write(configfile)