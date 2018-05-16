import ts3lib, ts3defines, datetime, time
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QTimer
from random import randint
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from bluscream import timestamp, clientURL, channelURL

class noCache(ts3plugin):
    name = "No Cache"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Auto Clear Teamspeak's Cache."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []

    def __init__(self):
        event_handler = LoggingEventHandler()
        self.observer = Observer()
        self.observer.schedule(event_handler, ts3lib.getConfigPath(), recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            self.observer.join()
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))
