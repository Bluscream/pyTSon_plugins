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
        if menuItemID != 0: return
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            self.printContacts()
        elif atype == ts3defines.PluginItemType.PLUGIN_CHANNEL:
            ts3lib.requestSendChannelTextMsg(schid, self.contactStats(), selectedItemID)
        elif atype == ts3defines.PluginItemType.PLUGIN_CLIENT:
            ts3lib.requestSendPrivateTextMsg(schid, self.contactStats(), selectedItemID)

    def processCommand(self, schid, command): self.printContacts(); return True

    def printContacts(self):
        ts3lib.printMessageToCurrentTab("{}{}".format(timestamp(), self.contactStats(True)))

    def contactStats(self,detailed=False):
        buddies = 0;blocked = 0;neutral = 0;unknown = 0
        female = 0;male = 0;soundboard = 0
        f_buddies = 0;m_buddies = 0
        f_blocked = 0;m_blocked = 0
        f_neutral = 0;m_neutral = 0
        f_unknown = 0;m_unknown = 0
        contacts = getContacts()
        if detailed:
            first = round(time.time()); last = 0
            firstc = None; lastc = None
        for contact in contacts:
            nick = contact["Nickname"].decode("utf-8").lower()
            if nick.startswith(self.cfg['filters']['Female Prefix']): female += 1
            elif nick.startswith(self.cfg['filters']['Male Prefix']): male += 1
            elif nick.startswith(self.cfg['filters']['Soundboard Prefix']): soundboard += 1
            status = contact["Friend"]
            if status == ContactStatus.FRIEND:
                buddies += 1
                if nick.startswith(self.cfg['filters']['Female Prefix']): f_buddies += 1
                elif nick.startswith(self.cfg['filters']['Male Prefix']): m_buddies += 1
            elif status == ContactStatus.BLOCKED:
                blocked += 1
                if nick.startswith(self.cfg['filters']['Female Prefix']): f_blocked += 1
                elif nick.startswith(self.cfg['filters']['Male Prefix']): m_blocked += 1
            elif status == ContactStatus.NEUTRAL:
                neutral += 1
                if nick.startswith(self.cfg['filters']['Female Prefix']): f_neutral += 1
                elif nick.startswith(self.cfg['filters']['Male Prefix']): m_neutral += 1
            else:
                unknown += 1
                if nick.startswith(self.cfg['filters']['Female Prefix']): f_unknown += 1
                elif nick.startswith(self.cfg['filters']['Male Prefix']): m_unknown += 1
            if "LastSeenEpoch" in contact and detailed:
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
                box_type.setCurrentText(tmp[1])
                box_type.addItems(["Prefix", "Suffix", "Contains", "Equals"])
                box_type.connect("currentIndexChanged(int)", self.currentIndexChanged)
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