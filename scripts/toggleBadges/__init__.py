from ts3plugin import ts3plugin
from random import choice, getrandbits
from PythonQt.QtCore import QTimer, Qt
from bluscream import timestamp, sendCommand, calculateInterval, AntiFloodPoints
import ts3defines, ts3lib

class toggleBadges(ts3plugin):
    name = "Hack the Badge"
    apiVersion = 21
    requestAutoload = False
    version = "1"
    author = "Bluscream"
    description = "Automatically sets some badges for you :)"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    debug = False
    timers = {}
    requested = False
    badges = [
        ("TeamSpeak Addon Author", "1cb07348-34a4-4741-b50f-c41e584370f7"),
        ("Gamescom 2016", "50bbdbc8-0f2a-46eb-9808-602225b49627"),
        ("Paris Games Week 2016", "d95f9901-c42d-4bac-8849-7164fd9e2310"),
        ("Gamescom 2014", "62444179-0d99-42ba-a45c-c6b1557d079a"),
        ("Paris Games Week 2014", "d95f9901-c42d-4bac-8849-7164fd9e2310"),
        ("TeamSpeak Addon Developer (Bronze)", "450f81c1-ab41-4211-a338-222fa94ed157"),
        ("TeamSpeak Addon Developer (Silver)", "c9e97536-5a2d-4c8e-a135-af404587a472"),
        ("TeamSpeak Addon Developer (Gold)", "94ec66de-5940-4e38-b002-970df0cf6c94"),
        ("Gamescom 2017", "534c9582-ab02-4267-aec6-2d94361daa2a"),
        ("Gamescom Hero 2017", "34dbfa8f-bd27-494c-aa08-a312fc0bb240"),
        ("MIFCOM", "7d9fa2b1-b6fa-47ad-9838-c239a4ddd116"),
        ("4Netplayers customer", "f81ad44d-e931-47d1-a3ef-5fd160217cf8"),
        ("Rocket Beans TV", "f22c22f1-8e2d-4d99-8de9-f352dc26ac5b")
    ]

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        for schid, timer in self.timers.items():
            self.stopTimer(schid)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        if schid in self.timers: self.stopTimer(schid)
        else: self.startTimer(schid)

    def tick(self):
        self.setRandomBadges()

    def onServerUpdatedEvent(self, schid):
        return # TODO: Check
        if not self.requested: return
        self.requested = False
        self.timers[schid] = QTimer()
        self.timers[schid].timeout.connect(self.tick)
        interval = calculateInterval(schid, AntiFloodPoints.CLIENTUPDATE, self.name)
        self.timers[schid].start(interval)

    def startTimer(self, schid):
        self.requested = True
        ts3lib.requestServerVariables(schid)

    def stopTimer(self, schid):
        if schid in self.timers:
            self.timers[schid].stop()
            del self.timers[schid]

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        return
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.startTimer(schid)
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
             self.stopTimer(schid)

    def setRandomBadges(self):
        rand = self.randomBadges()
        # overwolf = bool(getrandbits(1))
        badges = self.buildBadges(rand, True) # overwolf
        sendCommand(self.name, badges)#, schid) # TODO: ADD SCHID

    def randomBadges(self, count=3):
        badges = ""
        for i in range(0, count):
            badges += choice(self.badges)[1]
            if i != count-1: badges += ","
        return badges

    def buildBadges(self, badges, overwolf=False):
        return "clientupdate client_badges=overwolf={}:badges={}".format(1 if overwolf else 0, badges)
