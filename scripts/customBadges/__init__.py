from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer, Qt, QUrl, QFile, QIODevice
from PythonQt.QtSql import QSqlQuery
from PythonQt.QtGui import QWidget, QListWidgetItem, QIcon, QPixmap, QToolTip
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from bluscream import *
from os import path
from configparser import ConfigParser
from pytson import getPluginPath, getCurrentApiVersion
from pytsonui import setupUi
from json import load, loads
from traceback import format_exc
from re import compile
import ts3defines, ts3lib, ts3client

class customBadges(ts3plugin):
    name = "Custom Badges"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "0.9.4"
    author = "Bluscream"
    description = "Automatically sets some badges for you :)"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = "[b]Badges[/b]"
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Change " + name, "")# ,
        # (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Generate Badge UIDs", "")
    ]
    hotkeys = []
    ini = path.join(getPluginPath(), "scripts", "customBadges", "settings.ini")
    ui = path.join(getPluginPath(), "scripts", "customBadges", "badges.ui")
    icons = path.join(ts3lib.getConfigPath(), "cache", "badges")
    # icons_ext = path.join(icons, "external")
    badges_ext_remote = "https://raw.githubusercontent.com/R4P3-NET/CustomBadges/master/badges.json"
    cfg = ConfigParser()
    dlg = None
    cfg["general"] = {
        "cfgversion": "1",
        "debug": "False",
        "enabled": "True",
        "badges": "",
        "overwolf": "False",
        "lastnotice": ""
    }
    badges = {}
    extbadges = {}
    notice = QTimer()
    notice_nwmc = QNetworkAccessManager()
    def __init__(self):
        try:
            loadCfg(self.ini, self.cfg)
            (tstamp, self.badges, array) = loadBadges()
            self.requestBadgesExt()
            self.notice.timeout.connect(self.checkNotice)
            self.notice.start(30*1000)
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def infoData(self, schid, id, atype):
        if atype != ts3defines.PluginItemType.PLUGIN_CLIENT: return None
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID != id: return None
        # overwolf = self.cfg.getboolean('general', 'overwolf')
        # badges = self.cfg.get('general', 'badges').split(',')
        (err, badges) = ts3lib.getClientVariable(schid, id, ts3defines.ClientPropertiesRare.CLIENT_BADGES)
        (overwolf, badges) = parseBadges(badges)
        _return = ["Overwolf: {0}".format("[color=green]Yes[/color]" if overwolf else "[color=red]No[/color]")]
        # i = []
        # for badge in badges:
            # if badge
        for badge in badges:
            lst = self.badges
            if badge in self.extbadges: lst = self.extbadges
            _return.append("{} {}".format(
                # "[img]data://image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACp0lEQVR42qXSW0jTURwH8O/5/93mLm460alFXrKLqQ8aNUzRB6NWhOYG9ZDYlYiSHgoCs4d6qIwIiuipIOmtqClYUZEIhlDgbTIvealR7T6bm3Nz2///P/2bEURlRQd+L79zzuf8+HII/nOR5TYnduw+zjGMuuSJue2fgcltdRfT9BvO0kgY9pEPl8pedLb+NTCztb5cWZo3oM0GGI8PDi+B2xXauOl55+AfAZuhQQZ58pCudl0RlSiBJCmY0QFYJ4LjvEDK9M86ossDVQZjanXxI0VBOiSHWxI97vp5eF9bMOXjTTXdXebfAk5Dg4pZqZtPXasAL0+DvPlcoh+5eRns2zFMeHmE4kJKZcf90C8Be239Xc2eqgPEOQOiy4f82JlEP3ThFBjLMGJqHd5Me9sNfd0HfwKc2435is3F76TZFLHeV2BzC6Fsu5PYCx4yguvtgUq3Av2TPszMLhQ00dD7HwBX9c6+lNq8Lfz4EDi7ExJ9DVRX25eA5n3gerohS88BNx/H4yl7b+OCv+Y74JRkmGT1+oeyXBacKwAhMAd21Rqk3HqQAAL7d0KwWEEVadDwBFbHHPpn/aYjkaA5AXhyi9zKE9WZ/MgYaJIMiAsQnB+B1JzEC9zoINisQtAonyg1R2C22YN75/0a4ma0JxWnG26A84EGwqACheD1gl29Hqpr90Aog8BRE4RhCyDXgC7yUHHAp0AEXS53C/FXVMakxlIJb50Wvx0B5UXAaUdSeSVUbbe/ZdAkZvBSnCgDNMwDUQ5agcVTlwfkc0UVTW4qA52yAQJA4xwYsQSHGGRdI4hKjciVViRn5YFGqHhZABFLGiPocjiWQvQWl1CqlYVonAf3dQLxXDy6iLjNJpo8hMwcUFaGOMeD5wRxSgHu8KJql99DvgBZsjDj7AAlKgAAAABJRU5ErkJggg==[/img]",
                # "[img]file:///C:/Users/blusc/AppData/Roaming/TS3Client/styles/dark/apply.svg[/img]",
                "[img]https://badges-content.teamspeak.com/{}/{}.svg[/img]".format(badge, lst[badge]["filename"] if badge in lst else "unknown"),
                self.badgeNameByUID(badge, lst) if badge in lst else badge
            ))
        return _return

    def saveBadges(self, external):
        db = ts3client.Config()
        query = QSqlQuery(db)
        (timestamp, internal, array) = loadBadges()
        delimiter = array.mid(0, 12)
        delimiter1 = 0;delimiter2 = 0;delimiter3 = 0;delimiter4 = 0
        guid_len = 0;guid = ""
        name_len = 0;name = ""
        url_len = 0;url = ""
        desc_len = 0;desc = ""
        for i in range(0, array.size()):
            if i == 12: #guid_len
                guid_len = int(array.at(i))
                guid = str(array.mid(i+1, guid_len))
            elif i == (12 + 1 + guid_len + 1):
                delimiter1 = array.mid(i - 1,i - 1)
                name_len = int(array.at(i))
                name = str(array.mid(i+1, name_len))
            elif i == (12 + 1 + guid_len + 1 + name_len + 2):
                delimiter2 = array.mid(i - 1,i - 1)
                url_len = int(array.at(i))
                url = str(array.mid(i+1, url_len))
            elif i == (12 + 1 + guid_len + 1 + name_len + 2 + url_len + 2):
                delimiter3 = array.mid(i - 3,i - 3)
                delimiter4 = array.mid(i+desc_len,i+desc_len)
                desc_len = int(array.at(i))
                desc = str(array.mid(i+1, desc_len))
                break
        print("delimiter:", delimiter.toHex())
        print("delimiter1:", delimiter1.toHex())
        print("delimiter2:", delimiter2.toHex())
        print("delimiter3:", delimiter3.toHex())
        print("delimiter4:", delimiter4.toHex())
        print("array:", array.toHex())
        # query.prepare( "UPDATE Badges (BadgesListData) VALUES (:byteArray)" );
        # query.bindValue( ":imageData", array);

    def badgeNameByUID(self, uid, lst=badges):
        for badge in lst:
            if badge == uid: return lst[badge]["name"]

    def requestBadgesExt(self):
        self.nwmc_ext = QNetworkAccessManager()
        self.nwmc_ext.connect("finished(QNetworkReply*)", self.loadBadgesExt)
        self.nwmc_ext.get(QNetworkRequest(QUrl(self.badges_ext_remote)))

    def loadBadgesExt(self, reply):
        try:
            data = reply.readAll().data().decode('utf-8')
            self.extbadges = loads(data)
            self.nwmc_exti = {}; self.tmpfile = {}
            for badge in self.extbadges:
                _name = self.extbadges[badge]["filename"]
                _path = path.join(self.icons, _name)
                if path.exists(_path) and path.getsize(_path) > 0: continue
                self.requestExtIcon(_name)
                self.requestExtIcon("{}_details".format(_name))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def requestExtIcon(self, filename):
        self.nwmc_exti[filename] = QNetworkAccessManager()
        self.nwmc_exti[filename].connect("finished(QNetworkReply*)", self.loadExtIcon)
        self.tmpfile[filename] = QFile()
        self.tmpfile[filename].setFileName(path.join(self.icons,filename))
        self.tmpfile[filename].open(QIODevice.WriteOnly)
        url = "https://raw.githubusercontent.com/R4P3-NET/CustomBadges/master/img/{}".format(filename)
        self.nwmc_exti[filename].get(QNetworkRequest(QUrl(url)))

    def loadExtIcon(self, reply):
        try:
            if reply.error() != QNetworkReply.NoError:
                ts3lib.logMessage("Requesting \"{}\" failed:\n{}".format(reply.url().toString(),reply.errorString()), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0); return
            name = reply.url().fileName()
            self.tmpfile[name].write(reply.readAll())
            if self.tmpfile[name].isOpen():
                self.tmpfile[name].close()
                self.tmpfile[name].deleteLater()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def checkNotice(self):
        self.notice_nwmc.connect("finished(QNetworkReply*)", self.loadNotice)
        self.notice_nwmc.get(QNetworkRequest(QUrl("https://raw.githubusercontent.com/R4P3-NET/CustomBadges/master/notice")))

    def loadNotice(self, reply):
        data = reply.readAll().data().decode('utf-8')
        if data.strip() == "" or data == self.cfg.get('general', 'lastnotice'): return
        self.cfg.set('general', 'lastnotice', data)
        msgBox(data, 0, "{} Notice!".format(self.name))

    def stop(self):
        saveCfg(self.ini, self.cfg)
        self.notice.stop()

    def configure(self, qParentWidget):
        self.openDialog()

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL: return
        if menuItemID == 0: self.openDialog()
        elif menuItemID == 1:
            self.saveBadges(self.extbadges)
            for i in range(0,3):
                # 0c4u2snt-ao1m-7b5a-d0gq-e3s3shceript
                uid = [random_string(8, string.ascii_lowercase + string.digits)]
                for _i in range(0,3):
                    uid.append(random_string(4, string.ascii_lowercase + string.digits))
                uid.append(random_string(12, string.ascii_lowercase + string.digits))
                ts3lib.printMessageToCurrentTab("[color=red]Random UID #{}: [b]{}".format(i, '-'.join(uid)))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.setCustomBadges()

    def setCustomBadges(self):
        try:
            overwolf = self.cfg.getboolean('general', 'overwolf')
            badges = self.cfg.get('general', 'badges').split(",")
            # if len(badges) > 0: badges += ['0c4u2snt-ao1m-7b5a-d0gq-e3s3shceript']
            (err, schids) = ts3lib.getServerConnectionHandlerList()
            reg = compile('3(?:\.\d+)* \[Build: \d+\]')
            for schid in schids:
                _badges = badges
                err, ver = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_VERSION)
                err, platform = ts3lib.getServerVariable(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_PLATFORM)
                if getServerType(schid, reg) in [ServerInstanceType.TEASPEAK, ServerInstanceType.UNKNOWN]:
                    _badges = [x for x in badges if not x in self.extbadges][:3]
                _badges = buildBadges(_badges, overwolf)
                sendCommand(self.name, _badges, schid)
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def openDialog(self):
        if not self.dlg: self.dlg = BadgesDialog(self)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

class BadgesDialog(QWidget):
    listen = False
    def __init__(self, customBadges, parent=None):
        try:
            super(QWidget, self).__init__(parent)
            setupUi(self, customBadges.ui)
            self.cfg = customBadges.cfg
            self.ini = customBadges.ini
            self.badges = customBadges.badges
            self.extbadges = customBadges.extbadges
            self.icons = customBadges.icons
            # self.icons_ext = customBadges.icons_ext
            self.setCustomBadges = customBadges.setCustomBadges
            self.reloadPlugin = customBadges.__init__
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Customize Badges")
            self.setupList()
            self.listen = True
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def badgeItem(self, badge, alt=False, ext=False):
        try:
            lst = self.extbadges if ext else self.badges
            item = QListWidgetItem(lst[badge]["name"])
            item.setData(Qt.UserRole, badge)
            path = "{}\\{}".format(self.icons, lst[badge]["filename"])
            item.setToolTip('{}<br/><center><img width="64" height="64" src="{}_details">'.format(lst[badge]["description"], path))
            item.setIcon(QIcon("{}{}".format(path, "_details" if alt else "")))
            return item
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0); pass

    def updatePreview(self, uid, i, ext = False):
        try:
            if uid in self.badges: lst = self.badges
            elif uid in self.extbadges:
                lst = self.extbadges
                ext = True
            else: print("UID", uid, "not internal or external"); return
            # (QPixmap::fromImage(image.scaled(200,200))
            filename = "{}\\{}_details".format(self.icons, lst[uid]["filename"])
            if i == 0: badge = self.badge1
            elif i == 1: badge = self.badge2
            elif i == 2: badge = self.badge3
            else: return
            badge.setPixmap(QPixmap(filename).scaled(60,60))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def setupList(self):
        try:
            self.chk_overwolf.setChecked(True if self.cfg.getboolean('general', 'overwolf') else False)
            self.lst_available.clear()
            for badge in self.badges:
                self.lst_available.addItem(self.badgeItem(badge))
            self.grp_available.setTitle("{} Available (Internal)".format(len(self.badges)))
            self.lst_available_ext.clear()
            for badge in self.extbadges:
                self.lst_available_ext.addItem(self.badgeItem(badge, False, True))
            self.grp_available_ext.setTitle("{} Available (External)".format(len(self.extbadges)))
            badges = self.cfg.get('general', 'badges').split(",")
            if len(badges) < 1: return
            self.lst_active.clear()
            i = 0
            for badge in badges:
                if not badge: return
                if i < 3: self.updatePreview(badge, i)
                i += 1
                if badge in self.badges:
                    self.lst_active.addItem(self.badgeItem(badge))
                elif badge in self.extbadges:
                    self.lst_active.addItem(self.badgeItem(badge, False, True))
            self.grp_active.setTitle("{} Active".format(self.lst_active.count))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def updateBadges(self):
        try:
            items = []
            self.badge1.clear();self.badge2.clear();self.badge3.clear();
            for i in range(self.lst_active.count):
                 uid = self.lst_active.item(i).data(Qt.UserRole)
                 items.append(uid)
                 if i < 3: self.updatePreview(uid, i)
            self.grp_active.setTitle("{} Active".format(self.lst_active.count))
            self.cfg.set('general', 'badges', ','.join(items))
            self.setCustomBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)


    def addActive(self, ext=False):
        try:
            item = self.lst_available_ext.currentItem() if ext else self.lst_available.currentItem()
            self.lst_active.addItem(self.badgeItem(item.data(Qt.UserRole), False, True if ext else False))
            if self.chk_autoApply.checkState() == Qt.Checked:
                self.updateBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def delActive(self):
        try:
            row = self.lst_active.currentRow
            self.lst_active.takeItem(row)
            if self.chk_autoApply.checkState() == Qt.Checked:
                self.updateBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_lst_available_doubleClicked(self, mi):
        if not self.listen: return
        self.addActive()

    def on_btn_addactive_clicked(self):
        if not self.listen: return
        self.addActive()

    def on_lst_available_ext_doubleClicked(self, mi):
        if not self.listen: return
        self.addActive(True)

    def on_btn_addactive_ext_clicked(self):
        if not self.listen: return
        self.addActive(True)

    def on_lst_active_doubleClicked(self, mi):
        if not self.listen: return
        self.delActive()

    def on_btn_removeActive_clicked(self):
        if not self.listen: return
        self.delActive()

    def on_btn_removeAll_clicked(self):
        if not self.listen: return
        if not confirm("Custom Badge", "Remove all active badges?"): return
        self.lst_active.clear()
        if self.chk_autoApply.checkState() == Qt.Checked:
            self.updateBadges()

    def on_chk_overwolf_stateChanged(self, mi):
        if not self.listen: return
        try:
            self.cfg.set('general', 'overwolf', "True" if mi == Qt.Checked else "False")
            self.updateBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_lst_active_indexesMoved(self, mi):
        if not self.listen: return
        self.updateBadges()

    def on_lst_active_itemChanged(self, mi):
        if not self.listen: return
        self.updateBadges()

    def on_btn_apply_clicked(self):
        if not self.listen: return
        self.updateBadges()

    def on_btn_save_clicked(self):
        if not self.listen: return
        saveCfg(self.ini, self.cfg)

    def on_btn_reload_clicked(self):
        if not self.listen: return
        self.reloadPlugin(True)
        self.setupList()

    def on_btn_close_clicked(self):
        self.close()
