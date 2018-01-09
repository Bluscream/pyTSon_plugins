from ts3plugin import ts3plugin
from datetime import datetime
from random import choice, getrandbits
from PythonQt.QtCore import QTimer
import ts3defines, ts3lib

class autoBadges(ts3plugin):
    name = "Hack the Badge"
    apiVersion = 21
    requestAutoload = True
    version = "1"
    author = "Bluscream"
    description = "Automatically sets some badges for you :)"
    offersConfigure = False
    commandKeyword = "cmd"
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    debug = True
    timer = QTimer()
    interval = 1000
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

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        self.timer.timeout.connect(self.tick)
        self.timer.start(self.interval)
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(), self.name, self.author))

    def stop(self):
        if self.timer.isActive(): self.timer.stop()

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            if self.timer.isActive(): self.timer.stop()
            else: self.timer.start(self.interval)

    def tick(self):
        self.setRandomBadges()

    def setRandomBadges(self):
        rand = self.randomBadges()
        overwolf = True # bool(getrandbits(1))
        badges = self.buildBadges(rand, overwolf)
        self.sendCommand(badges)

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.setRandomBadges()

    def randomBadges(self, count=3):
        badges = ""
        for i in range(0, count):
            badges += choice(self.badges)[1]
            if i != count-1: badges += ","
        return badges

    def buildBadges(self, badges, overwolf=False):
        return "clientupdate client_badges=overwolf={}:badges={}".format(1 if overwolf else 0, badges)

    def sendCommand(self, cmd):
        ts3lib.printMessageToCurrentTab("[color=white]Sending command: {}".format(cmd))
        cmd = cmd.replace(" ", "~s")
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        ts3lib.requestSendServerTextMsg(schid, "~cmd{}".format(cmd))

    def processCommand(self, schid, cmd):
        cmd = cmd.split(' ', 1)
        command = cmd[0].lower()
        if command == "randombadges": self.sendCommand(self.randomBadges())
        return 1
