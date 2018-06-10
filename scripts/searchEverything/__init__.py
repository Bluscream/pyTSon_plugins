from os import path
from datetime import datetime
from PythonQt.QtCore import QUrl
from PythonQt.QtGui import QDesktopServices
from ts3plugin import ts3plugin
from pluginhost import PluginHost
from traceback import format_exc
import ts3defines, ts3lib, pytson
from urllib.parse import quote_plus

class searchEverything(ts3plugin):
    name = "Search"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 21
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Let's you quickyly search for all kinds of stuff"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "== {0} ==".format(name), ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 1, "Nickname (TSViewer)", "scripts/%s/tsviewer.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 2, "Nickname (GameTracker)", "scripts/%s/gametracker.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 3, "Nickname (TS3Index)", "scripts/%s/ts3index.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 4, "Nickname (Google)", "scripts/%s/google.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 5, "Profile (GameTracker)", "scripts/%s/gametracker.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 6, "UID (TS3Index)", "scripts/%s/ts3index.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 7, "UID (Google)", "scripts/%s/google.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 8, "Owner (TSViewer)", "scripts/%s/tsviewer.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 9, "Badges (TS3Index)", "scripts/%s/ts3index.png"%__name__),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 10, "== {0} ==".format(name), "")
    ]

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def menuCreated(self):
        if not self.name in PluginHost.active: return
        for id in [0,10]:
            try: ts3lib.setPluginMenuEnabled(PluginHost.globalMenuID(self, id), False)
            except: pass

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        try:
            url = ""
            if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
                if menuItemID == 1: # Nickname (TSViewer)
                    url = "http://www.tsviewer.com/index.php?page=search&action=ausgabe_user&nickname=%%CLIENT_NAME_PERCENT_ENCODED%%"
                elif menuItemID == 2: # Nickname (GameTracker)
                    url = "http://www.gametracker.com/search/?search_by=online_offline_player&query=%%CLIENT_NAME_PERCENT_ENCODED%%"
                elif menuItemID == 3: # Nickname (TS3Index)
                    url = "http://ts3index.com/?page=searchclient&nickname=%%CLIENT_NAME_PERCENT_ENCODED%%"
                elif menuItemID == 4: # Nickname (Google)
                    url = "https://www.google.com/search?q=%%CLIENT_NAME_PERCENT_ENCODED%%"
                elif menuItemID == 5: # Profil (GameTracker)
                    url = "http://www.gametracker.com/search/?search_by=profile_username&query=%%CLIENT_NAME_PERCENT_ENCODED%%"
                elif menuItemID == 6: # UID (TS3Index)
                    url = "http://ts3index.com/?page=searchclient&uid=%%CLIENT_UNIQUE_ID%%"
                elif menuItemID == 7: # UID (Google)
                    url = "https://www.google.com/search?q=%%CLIENT_UNIQUE_ID%%"
                elif menuItemID == 8: # Besitzer (TSViewer)
                    url = "http://www.tsviewer.com/index.php?page=search&action=ausgabe&suchbereich=ansprechpartner&suchinhalt=%%CLIENT_NAME_PERCENT_ENCODED%%"
                elif menuItemID == 9: # Badges (TS3Index)
                    url = "https://ts3index.com/?page=searchclient&badges=%%CLIENT_BADGES%%"
                else: return
                # payload = {'username':'administrator', 'password':'xyz'}
                # nickname_encoded = urlencode(nickname, quote_via=quote_plus)
                # nickname_encoded = nickname_encoded.replace("+", "%2B").replace("/", "%2F").replace("=", "%3D")
                if "%%CLIENT_NAME_PERCENT_ENCODED%%" in url:
                    (err, nickname) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_NICKNAME)
                    url = url.replace("%%CLIENT_NAME_PERCENT_ENCODED%%", quote_plus(nickname))
                if "%%CLIENT_UNIQUE_ID%%" in url:
                    (err, uid) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
                    url = url.replace("%%CLIENT_UNIQUE_ID%%", quote_plus(uid))
                if "%%CLIENT_BADGES%%" in url:
                    (err, badges) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientPropertiesRare.CLIENT_BADGES)
                    url = url.replace("%%CLIENT_BADGES%%", badges)
            else: return
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("Opening URL: \"{}\"".format(url))
            QDesktopServices.openUrl(QUrl(url))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)
