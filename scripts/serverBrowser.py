from ts3plugin import ts3plugin, PluginHost
from pytsonui import setupUi, getValues, ValueType
from PythonQt.QtGui import QDialog, QListWidgetItem, QWidget, QComboBox, QPalette, QTableWidgetItem, QMenu, QAction, QCursor, QApplication
from PythonQt.QtCore import Qt, QTimer
from datetime import datetime
import ts3, ts3defines, os, requests, json, configparser, webbrowser, traceback, urllib.parse


class serverBrowser(ts3plugin):
    name = "Better Server Browser"
    apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "A better serverlist provided by PlanetTeamspeak.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = ""
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Browse Servers", "scripts/serverBrowser/gfx/icon.png"),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "View on PT", "")]
    hotkeys = []
    debug = False
    ini = os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "serverBrowser", "cfg", "serverBrowser.ini")
    config = configparser.ConfigParser()

    def __init__(self):
        if os.path.isfile(self.ini):
            self.config.read(self.ini)
            #for key, value in self.config["FILTERS"].items():
                #ts3.printMessageToCurrentTab(str(key).title()+": "+str(value))
        else:
            self.config['GENERAL'] = { "debug": "False", "api": "https://api.planetteamspeak.com/", "morerequests": "False", "serversperpage": "100" }
            self.config['FILTERS'] = {
                "serverNameModifier": "Contains", "filterServerName": "", "countryBox": "",
                "hideEmpty": "False", "hideFull": "False", "maxUsers": "False", "maxUsersMin": "0", "maxUsersMax": "0",
                "maxSlots": "False", "maxSlotsMin": "0", "maxSlotsMax": "0", "filterPassword": "all", "filterChannels": "all"
            }
            with open(self.ini, 'w') as configfile:
                self.config.write(configfile)
        ts3.printMessageToCurrentTab(str(QApplication.instance()))

        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.config['GENERAL']['debug'] == "True":
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]Bluscream[/url] loaded.")

    def configure(self, qParentWidget):
        d = dict()
        d['debug'] = (ValueType.boolean, "Debug", self.config['GENERAL']['debug'] == "True", None, None)
        d['morerequests'] = (ValueType.boolean, "Fast Connection", self.config['GENERAL']['morerequests'] == "True", None, None)
        d['serversperpage'] = (ValueType.integer, "Servers per page:", int(self.config['GENERAL']['serversperpage']), 0, 250)
        d['api'] = (ValueType.string, "API Base URL:", self.config['GENERAL']['api'], None, 1)
        widgets = getValues(None, "Server Browser Settings", d, self.configDialogClosed)

    def configDialogClosed(self, r, vals):
        if r == QDialog.Accepted:
            self.config['GENERAL'] = { "debug": str(vals['debug']), "api": vals['api'], "morerequests": str(vals['morerequests']), "serversperpage": str(vals['serversperpage']) }
            with open(self.ini, 'w') as configfile:
                self.config.write(configfile)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0:
                self.dlg = ServersDialog(self)
                self.dlg.show()
                #ts3.printMessageToCurrentTab(str(self.filters))
            elif menuItemID == 1:
                _schid = ts3.getCurrentServerConnectionHandlerID()
                (error, _clid) = ts3.getClientID(_schid)
                (error, _ip) = ts3.getConnectionVariableAsString(_schid,_clid,ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
                (error, _port) = ts3.getConnectionVariableAsString(_schid,_clid,ts3defines.ConnectionProperties.CONNECTION_SERVER_PORT)
                url = ""
                if _port != "":
                    _url = self.config['GENERAL']['api']+"serverlist/result/server/ip/"+_ip+":"+_port+"/"
                else:
                    _url = self.config['GENERAL']['api']+"serverlist/result/server/ip/"+_ip+"/"
                ts3.printMessageToCurrentTab(str("Navigating to \""+_url+"\""))
                webbrowser.open(_url)

class ServersDialog(QDialog):
    page = 1
    pages = 0
    cooldown = False
    cooldown_page = False
    cooldown_time = 5000
    cooldown_time_page = 1000
    countries = []
    NAME_MODIFIERS = ["Contains", "Starts with", "Ends with"]
    CONF_WIDGETS = [
                        ("serverList", True, []),
                        ("serverNameModifier", True, []),
                        ("filterServerName", True, []),
                        ("locationGroup", False, [
                            ("countryBox", True, [])
                        ]),
                        ("usersGroup", False, [
                            ("hideEmpty", True, []),
                            ("hideFull", True, []),
                            ("maxUsers", True, []),
                            ("maxUsersMin", True, []),
                            ("maxUsersMax", True, [])
                        ]),
                        ("slotsGroup", False, [
                            ("maxSlots", True, []),
                            ("maxSlotsMin", True, []),
                            ("maxSlotsMax", True, [])
                        ]),
                        ("passwordGroup", False, [
                            ("filterPasswordShowAll", True, []),
                            ("filterPasswordShowWith", True, []),
                            ("filterPasswordShowWithout", True, [])
                        ]),
                        ("channelsGroup", False, [
                            ("filterChannelsCanCreate", True, []),
                            ("filterChannelsCantCreate", True, []),
                            ("filterChannelsShowAll", True, [])
                        ]),
                        ("status", True, []),
                        ("info", True, []),
                        ("pageLabel", True, []),
                        ("apply", True, []),
                        ("reload", True, []),
                        ("previous", True, []),
                        ("next", True, [])
                    ]
    def buhl(self, s):
        if s.lower() == 'true' or s == 1:
            return True
        elif s.lower() == 'false' or s == 0:
            return False
        else:
            raise ValueError("Cannot convert {} to a bool".format(s))

    def __init__(self,serverBrowser, parent=None):
        self.serverBrowser=serverBrowser
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "serverBrowser", "ui", "servers.ui"), self.CONF_WIDGETS)
        self.setWindowTitle("PlanetTeamspeak Server Browser")
        #ts3.printMessageToCurrentTab("Countries: "+str(self.countries))
        #try:
            #self.serverList.doubleClicked.connect(self.table_doubleclicked)
            #self.serverList.connect("doubleClicked()", self.table_doubleclicked)
            #self.apply.connect("clicked()", self.on_apply_clicked)
            #self.reload.connect("clicked()", self.on_reload_clicked)
        #except:
            #ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
        #self.ReasonList.connect("currentItemChanged(QListWidgetItem*, QListWidgetItem*)", self.onReasonListCurrentItemChanged)
        #self.ReasonList.connect("itemChanged(QListWidgetItem*)", self.onReasonListItemChanged)
        self.serverList.horizontalHeader().setStretchLastSection(True)
        self.serverList.setColumnWidth(0, 300)
        self.serverNameModifier.addItems(self.NAME_MODIFIERS)
        self.pageLabel.mousePressEvent = self.on_pageLabel_clicked
        #self.cfg.set("general", "differentApi", "True" if state == Qt.Checked else "False")
        self.requestAvailableCountries()
        self.countryBox.addItems([x[1]+" ("+str(x[2])+")" for x in self.countries])
        #ReportDialog.ReasonList.clear()
        self.setupFilters()
        # self.serverList.doubleClicked.connect(self.doubleClicked_table)
        #ts3.printMessageToCurrentTab(str(serverBrowser.filters))
        #if serverBrowser.filters.filterServerName != "":
            #self.filterServerName.setText(serverBrowser.filters.filterServerName)
        #item.setFlags(item.flags() &~ Qt.ItemIsEditable)
        # self.countryBox.clear()
        #for item in countries:
            #self.countryBox.addItem(str(item[1]))
        #self.serverList.setStretchLastSection(true)
        self.listServers()

    def setupFilters(self):
        try:
            _filters = self.serverBrowser.config["FILTERS"]
            buhl = self.buhl
            self.hideEmpty.setChecked(buhl(_filters["hideEmpty"]))
            self.hideFull.setChecked(buhl(_filters["hideFull"]))
            self.maxUsers.setChecked(buhl(_filters["maxUsers"]))
            self.maxUsersMin.setValue(int(_filters["maxUsersMin"]))
            self.maxUsersMax.setValue(int(_filters["maxUsersMax"]))
            self.maxSlots.setChecked(buhl(_filters["maxSlots"]))
            self.maxSlotsMin.setValue(int(_filters["maxSlotsMin"]))
            self.maxSlotsMax.setValue(int(_filters["maxSlotsMax"]))
            if _filters["filterPassword"] == "none":
                self.filterPasswordShowWithout.setChecked(True)
                #self.filterPasswordShowWith.setChecked(False)
                #self.filterPasswordShowAll.setChecked(False)
            elif _filters["filterPassword"] == "only":
                #self.filterPasswordShowWithout.setChecked(False)
                self.filterPasswordShowWith.setChecked(True)
                #self.filterPasswordShowAll.setChecked(False)
            else:
                #self.filterPasswordShowWithout.setChecked(False)
                #self.filterPasswordShowWith.setChecked(False)
                self.filterPasswordShowAll.setChecked(True)
            if _filters["filterChannels"] == "none":
                self.filterChannelsCantCreate.setChecked(True)
                #self.filterChannelsCanCreate.setChecked(False)
                #self.filterChannelsShowAll.setChecked(False)
            elif _filters["filterChannels"] == "only":
                #self.filterChannelsCantCreate.setChecked(False)
                self.filterChannelsCanCreate.setChecked(True)
                #self.filterChannelsShowAll.setChecked(False)
            else:
                #self.filterChannelsCantCreate.setChecked(False)
                #self.filterChannelsCanCreate.setChecked(False)
                self.filterChannelsShowAll.setChecked(True)
            self.serverNameModifier.setCurrentText(_filters["serverNameModifier"])
            self.filterServerName.setText(_filters["filterServerName"])
            #self.countryBox.setCurrentText(self.countryBox.findText(_filters["countryBox"]).split(" (")[0])
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def contextMenuEvent(self, event):
        try:
            self.menu = QMenu(self.serverList)
            connectAction = QAction('Connect', self)
            #connectAction.triggered.connect(self.connect)
            self.menu.addAction(connectAction)
            self.menu.popup(QCursor.pos())
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def connect(self):
        index = self.serverList.selectedIndexes()[0]
        id_us = int(self.serverList.model().data(index).toString())
        ts3.printMessageToCurrentTab("index : " + str(id_us))

    def getCountryIDbyName(self, name):
        try:
            if name.__contains__(" ("):
                name = name.split(" (")[0]
            return [c for c in self.countries if c[1]==name][0][0]
        except:
            return '--'

    def getCountryNamebyID(self, cid):
        try:
            return [c for c in self.countries if c[0]==cid][0][1]
        except:
            return 'Unknown ('+cid+')'

    def requestAvailableCountries(self):
        countries = requests.get(self.serverBrowser.config['GENERAL']['api']+"servercountries")
        self.status.setText("Response from \""+self.serverBrowser.config['GENERAL']['api']+"\": "+str(countries.status_code)+": "+countries.reason)
        palette = QPalette()
        if countries.status_code == 200:
            palette.setColor(QPalette.Foreground,Qt.darkGreen)
            self.countryBox.clear()
        else:
            palette.setColor(QPalette.Foreground,Qt.red)
        self.status.setPalette(palette)
        countries = countries.content.decode('utf-8')
        countries = json.loads(countries)["result"]["data"]
        y= sum(x[2] for x in countries)
        #y = 0
        #for x in countries:
        #   y = y + x[2]
        #ts3.printMessageToCurrentTab(str(countries))
        if "-" in [h[0] for h in countries] or "--" in [h[0] for h in countries]:
            countries = countries[0:1]+sorted(countries[1:],key=lambda x: x[1])
        else:
            countries = sorted(countries,key=lambda x: x[1])
        self.countries = [['ALL', 'All', y]]+countries


        #__countries = __countries.__add__([['ALL', 'All', 0]])
        # ts3.printMessageToCurrentTab(str(countries))

    def setupURL(self):
        # import urllib
        # f = { 'eventName' : 'myEvent', 'eventDescription' : "cool event"}
        # urllib.urlencode(f)
        _filters = self.serverBrowser.config["FILTERS"]
        url = self.serverBrowser.config['GENERAL']['api']+"serverlist/?page="+str(self.page)+"&limit="+str(self.serverBrowser.config['GENERAL']['serversperpage'])
        if _filters["filterPassword"] == "none":
            url += "&password=false"
        elif _filters["filterPassword"] == "only":
            url += "&password=true"
        if _filters["filterChannels"] == "none":
            url += "&createchannels=false"
        elif _filters["filterChannels"] == "only":
            url += "&createchannels=true"
        if self.buhl(_filters["maxUsers"]):
            url += "&minusers="+str(_filters["maxUsersMin"])+"&maxusers="+str(_filters["maxUsersMax"])
        if self.buhl(_filters["maxSlots"]):
            url += "&minslots="+str(_filters["maxSlotsMin"])+"&maxslots="+str(_filters["maxSlotsMax"])
        if _filters["filterServerName"] and _filters["filterServerName"] != "":
            url += "&search="+urllib.parse.quote_plus(_filters["filterServerName"])
        cid = self.getCountryIDbyName(_filters["countryBox"])
        if _filters["countryBox"] != "All" and cid != '--':
            url+= "&country="+cid
        if self.serverBrowser.config["GENERAL"]["debug"] == "True":
            ts3.printMessageToCurrentTab(url)
        return url

    def requestServers(self, url):
        servers = requests.get(url)
        self.status.setText("Response from \""+self.serverBrowser.config['GENERAL']['api']+"\": "+str(servers.status_code)+": "+servers.reason)
        palette = QPalette()
        if not servers.status_code == 200:
            palette.setColor(QPalette.Foreground,Qt.red)
        self.status.setPalette(palette)
        _servers = servers.content.decode('utf-8')
        __servers = json.loads(_servers)
        return __servers

    def listServers(self):
        ts3.printMessageToCurrentTab(str(self.cooldown))
        if self.cooldown:
            self.status.setText("You have to wait "+str(self.cooldown_time/1000)+" second(s) before retrying!")
            palette = QPalette()
            palette.setColor(QPalette.Foreground,Qt.red)
            self.status.setPalette(palette)
            return
        url = self.setupURL()
        servers = self.requestServers(url)
        self.status.setText("Status: "+servers["status"].title())
        if servers["status"] == "success":
            self.pageLabel.setText(str(servers["result"]["pageactive"])+" / "+str(servers["result"]["pagestotal"]))
            self.info.setText(str(servers["result"]["itemsshown"])+" / "+str(servers["result"]["itemstotal"])+" Servers shown.")
            self.serverList.setRowCount(0)
        elif servers["status"] == "error":
            self.info.setText("Requested Page: "+str(self.page))
            self.status.setText(servers["status"].title()+": "+servers["result"]["message"]+" ("+str(servers["result"]["code"])+")")
            palette = QPalette()
            palette.setColor(QPalette.Foreground,Qt.red)
            self.status.setPalette(palette)
            return
        else:
            self.info.setText("Requested Page: "+str(self.page))
            palette = QPalette()
            palette.setColor(QPalette.Foreground,Qt.red)
            self.status.setPalette(palette)
            return
        _list = self.serverList
        _filters = self.serverBrowser.config["FILTERS"]
        if servers["result"]["pageactive"] == 1:
            self.previous.setEnabled(False)
        else:
            self.previous.setEnabled(True)
        if servers["result"]["pageactive"] == servers["result"]["pagestotal"]:
            self.next.setEnabled(False)
        else:
            self.next.setEnabled(True)
        for key in servers["result"]["data"]:
            if self.buhl(_filters["hideFull"]) and key["users"] >= key["slots"]:
                continue
            elif self.buhl(_filters["hideEmpty"]) and key["users"] <= 0:
                continue
            else:
                rowPosition = _list.rowCount
                _list.insertRow(rowPosition)
                # if key['premium']:
                #     _list.setItem(rowPosition, 0, QTableWidgetItem("Yes"))
                # else:
                #     _list.setItem(rowPosition, 0, QTableWidgetItem("No"))
                _list.setItem(rowPosition, 0, QTableWidgetItem(key['name']))
                _list.setItem(rowPosition, 1, QTableWidgetItem(str(key['users'])+' / '+str(key['slots'])))
                if key['users'] >= key['slots']:
                    palette = QPalette()
                    palette.setColor(QPalette.Foreground,Qt.red)
                    _list.setPalette(palette)
                _list.setItem(rowPosition, 2, QTableWidgetItem(self.getCountryNamebyID(key['country'])))
                #ts3.printMessageToCurrentTab(str(key['createchannels']))
                if key['createchannels']:
                    _list.setItem(rowPosition, 3, QTableWidgetItem("Yes"))
                else:
                    _list.setItem(rowPosition, 3, QTableWidgetItem("No"))
                if key['password']:
                    _list.setItem(rowPosition, 4, QTableWidgetItem("Yes"))
                else:
                    _list.setItem(rowPosition, 4, QTableWidgetItem("No"))

    #def onReasonListItemChanged(self, item):
        #checked = item.checkState() == Qt.Checked
        #name = item.data(Qt.UserRole)

        #if checked and name not in self.host.active:
            #self.host.activate(name)
        #elif not checked and name in self.host.active:
            #self.host.deactivate(name)

        #if self.pluginsList.currentItem() == item:
            #self.settingsButton.setEnabled(checked and name in self.host.active and self.host.active[name].offersConfigure)

    def disable_cooldown(self):
        self.cooldown = False
        self.reload.setEnabled(True)

    def disable_cooldown_page(self):
        self.cooldown_page = False
        self.previous.setEnabled(True)
        self.next.setEnabled(True)

    def on_apply_clicked(self):
        try:
            self.serverBrowser.config.set("FILTERS", "hideEmpty", str(self.hideEmpty.isChecked()))
            self.serverBrowser.config.set("FILTERS", "hideFull", str(self.hideFull.isChecked()))
            self.serverBrowser.config.set("FILTERS", "maxUsers", str(self.maxUsers.isChecked()))
            self.serverBrowser.config.set("FILTERS", "maxUsersMin", str(self.maxUsersMin.value))
            self.serverBrowser.config.set("FILTERS", "maxUsersMax", str(self.maxUsersMax.value))
            self.serverBrowser.config.set("FILTERS", "maxSlots", str(self.maxSlots.isChecked()))
            self.serverBrowser.config.set("FILTERS", "maxSlotsMin", str(self.maxSlotsMin.value))
            self.serverBrowser.config.set("FILTERS", "maxSlotsMax", str(self.maxSlotsMax.value))
            if self.filterPasswordShowWithout.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterPassword", "none")
            elif self.filterPasswordShowWith.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterPassword", "only")
            elif self.filterPasswordShowAll.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterPassword", "all")
            if self.filterChannelsCantCreate.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterChannels", "none")
            elif self.filterChannelsCanCreate.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterChannels", "only")
            elif self.filterChannelsShowAll.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterChannels", "all")
            self.serverBrowser.config.set("FILTERS", "serverNameModifier", self.serverNameModifier.currentText)
            self.serverBrowser.config.set("FILTERS", "filterServerName", self.filterServerName.text)
            self.serverBrowser.config.set("FILTERS", "countryBox", self.countryBox.currentText.split(" (")[0])
            with open(self.serverBrowser.ini, 'w') as configfile:
                self.serverBrowser.config.write(configfile)
            if self.buhl(self.serverBrowser.config['GENERAL']['morerequests']):
                self.requestAvailableCountries()
                self.countryBox.addItems([x[1]+" ("+str(x[2])+")" for x in self.countries])
            self.page = 1
            self.listServers()
            if not self.cooldown:
                self.cooldown = True
                QTimer.singleShot(self.cooldown_time, self.disable_cooldown)
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_reload_clicked(self):
        try:
            self.listServers()
            if not self.cooldown:
                self.cooldown = True
                self.reload.setEnabled(False)
                QTimer.singleShot(self.cooldown_time, self.disable_cooldown)
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def on_previous_clicked(self):
        try:
            if self.cooldown_page:
                self.status.setText("You have to wait "+str(self.cooldown_time_page/1000)+" second(s) before switching pages!")
                palette = QPalette()
                palette.setColor(QPalette.Foreground,Qt.red)
                self.status.setPalette(palette)
                return
            if self.page > 1:
                self.page -= 1
                self.listServers()
            if not self.cooldown:
                self.cooldown_page = True
                self.previous.setEnabled(False)
                self.next.setEnabled(False)
                QTimer.singleShot(self.cooldown_time_page, self.disable_cooldown_page)
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def on_next_clicked(self):
        try:
            if self.cooldown_page:
                self.status.setText("You have to wait "+str(self.cooldown_time_page/1000)+" second(s) before switching pages!")
                palette = QPalette()
                palette.setColor(QPalette.Foreground,Qt.red)
                self.status.setPalette(palette)
                return
            self.page += 1
            self.listServers()
            if not self.cooldown:
                self.cooldown_page = True
                self.previous.setEnabled(False)
                self.next.setEnabled(False)
                QTimer.singleShot(self.cooldown_time_page, self.disable_cooldown_page)
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def on_serverList_doubleClicked(self):
        try:
            ts3.logMessage("test", ts3defines.LogLevel.LogLevel_INFO, "pyTSon", 0)
            index = self.serverList.selectedIndexes()[0]
            ts3.logMessage("test2", ts3defines.LogLevel.LogLevel_INFO, "pyTSon", 0)
            # id_us = int(self.serverList.model().data(index).toString())
            # ts3.printMessageToCurrentTab("index : " + str(id_us))
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_pageLabel_clicked(self, event):
        try:
            ts3.logMessage("test", ts3defines.LogLevel.LogLevel_INFO, "pyTSon", 0)
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
