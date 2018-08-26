import ts3defines, ts3lib, pytson
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from bluscream import timestamp, getScriptPath, getIDByName # , getChannelPassword
from ts3enums import ServerTreeItemType
from PythonQt.Qt import QApplication

from re import search, sub, IGNORECASE
from calculator import NumericStringParser
from bluscream import inputBox

def getChannelPassword(schid:int, cid:int, crack:bool=False, ask:bool=False, calculate:bool=False):
    """
    Tries several methods to get the channel password.
    :param calculate: Wether to try to solve math riddles
    :param schid: serverConnectionHandlerID
    :param cid: channelID of the target channel
    :param crack: wether to try a dictionary attack on the channel to get the password
    :param ask: wether to ask the user for the password in case he knows
    :return password: the possible password
    """
    # type: (int, int, bool, bool, bool) -> str
    (err, passworded) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_FLAG_PASSWORD)
    if err != ts3defines.ERROR_ok or not passworded:
        return False
    (err, path, pw) = ts3lib.getChannelConnectInfo(schid, cid)
    if pw:
        return pw
    (err, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
    if err != ts3defines.ERROR_ok or not name: return err
    name = name.strip()
    pattern = r"(?:pw|pass(?:wor[dt])?)[|:=]?\s*(.*)"
    # pattern = r"^.*[kennwort|pw|password|passwort|pass|passwd](.*)$"
    regex = search(pattern, name, IGNORECASE)
    if regex:
        result = regex.group(1).strip()
        result = sub(r"[)|\]|\}]$", "", result)
        if calculate:
            math_chars = ["/","%","+","-","^","*"]
            for math_char in math_chars:  # any(i in result for i in math_chars):
                has_char = math_char in result
                if has_char:
                    nsp = NumericStringParser()
                    result = str(round(nsp.eval(result)))
                    break
        return result
    # if name.isdigit(): return name
    last = name.split(" ")[-1]
    if last.isdigit():
        return last
    if crack:
        active = PluginHost.active
        if "PW Cracker" in active: active["PW Cracker"].onMenuItemEvent(schid,
                                                                        ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL,
                                                                        1, cid)
    if ask:
        pw = inputBox("Enter Channel Password", "Password:", name)
        return pw
    return name

class treeView(ts3plugin):
    path = getScriptPath(__name__)
    name = "Tree View Test"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "tv"
    infoTitle = None
    menuItems = []
    hotkeys = [
        ("tree_view_selected_name", "Print Selected name to current tab"),
        ("tree_view_message_selected", "Message selected client, channel or server")
    ]
    app = QApplication.instance()
    servertree = None

    def widget(self, name):
        widgets = self.app.allWidgets()
        for x in widgets:
            if str(x.objectName) == name:
                return x

    def __init__(self):
        self.setAnimated()
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def setAnimated(self):
        try:
            self.servertree = self.widget("ServerTreeView")
            if self.servertree is None: return
            if not self.servertree.isAnimated():
                self.servertree.setAnimated(True)
        except: pass

    def processCommand(self, schid, keyword): self.onHotkeyOrCommandEvent(keyword, schid)
    def onHotkeyEvent(self, keyword): self.onHotkeyOrCommandEvent(keyword)
    def onHotkeyOrCommandEvent(self, keyword, schid=0):
        if not self.app.activeWindow().className() == "MainWindow": return
        if not schid: schid = ts3lib.getCurrentServerConnectionHandlerID()
        # print(self.name, "> servertree:", self.servertree)
        selected = self.servertree.currentIndex()
        if not selected: return
        # print(self.name, "> selected:", selected)
        name = selected.data()
        item = getIDByName(name, schid)
        if keyword == "tree_view_selected_name":
            # print(self.name, "> dir(selected):", dir(selected))
            # print(self.name, "> selected.flags():", selected.flags())
            # print(self.name, "> selected.internalId():", selected.internalId())
            # print(self.name, "> selected.internalPointer():", selected.internalPointer())
            # print(self.name, "> selected.row():", selected.row())
            ts3lib.printMessageToCurrentTab("[b]Selected Item: \"{}\"\nType: {} ID: {}".format(name, item[1], item[0]))
        elif keyword == "tree_view_message_selected":
            msg = " "
            if item[1] == ServerTreeItemType.SERVER:
                ts3lib.requestSendServerTextMsg(schid, msg)
            elif item[1] == ServerTreeItemType.CHANNEL:
                (err, clid) = ts3lib.getClientID(schid)
                (err, cid) = ts3lib.getChannelOfClient(schid, clid)
                if cid != item[0]:
                    pw = getChannelPassword(schid, item[0])
                    ts3lib.printMessageToCurrentTab("{} > PW: {}".format(self.name, pw))
                    err = ts3lib.requestClientMove(schid, clid, item[0], pw if pw else "123")
                if not err: ts3lib.requestSendChannelTextMsg(schid, msg, 0)
            elif item[1] == ServerTreeItemType.CLIENT:
                ts3lib.requestSendPrivateTextMsg(schid, msg, item[0])
        elif keyword == "tree_view_enter_channel":
            if item[1] != ServerTreeItemType.CHANNEL: return
            (err, clid) = ts3lib.getClientID(schid)
            (err, cid) = ts3lib.getChannelOfClient(schid, clid)
            if cid == item[0]: return
            pw = getChannelPassword(schid, item[0], calculate=True)
            ts3lib.printMessageToCurrentTab("{} > PW: {}".format(self.name, pw))
            ts3lib.requestClientMove(schid, clid, item[0], pw if pw else "123")

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus != ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED: return
        self.setAnimated()