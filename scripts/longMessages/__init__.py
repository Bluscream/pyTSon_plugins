from PythonQt.QtGui import QMessageBox, QWidget, QInputDialog
from PythonQt.Qt import QApplication
from ts3plugin import ts3plugin
import datetime, ts3defines, ts3lib

class longMessages(ts3plugin):
    name = "Long Messages"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "A simple script that splits up long texts into multiple messages for you."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Message to Channel", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 0, "Message to Channel", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Message to Client", "")]
    hotkeys = []
    debug = False
    maxsize = 900

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab( '{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.'.format(self.timestamp(), self.name, self.author))

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL and menuItemID == 0:
            error, ownid = ts3lib.getClientID(schid)
            if not error == ts3defines.ERROR_ok: _t = QMessageBox(QMessageBox.Critical, "Error #%s" % error,"Unable to get own client ID in Tab #%s!"%schid);_t.show();return
            error, ownchan = ts3lib.getChannelOfClient(schid, ownid)
            if not error == ts3defines.ERROR_ok: _t = QMessageBox(QMessageBox.Critical, "Error #%s" % error,"Unable to get own channel ID in Tab #%s!"%schid);_t.show();return
            self.sendMessage(schid, ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL, ownchan)
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT and menuItemID == 0:
            self.sendMessage(schid, ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT, selectedItemID)
        elif atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL and menuItemID == 0:
            self.sendMessage(schid, ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL, selectedItemID)

    def sendMessage(self, schid, targetMode, toID):
        x = QWidget()
        clipboard = QApplication.clipboard().text();
        _message = QInputDialog.getMultiLineText(x, "Enter long text here", "", clipboard)
        message = [_message[i:i + self.maxsize] for i in range(0, len(_message), self.maxsize)]
        if targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CHANNEL:
            for msg in message:
                error = ts3lib.requestSendChannelTextMsg(schid, "\n"+msg, toID)
                if not error == ts3defines.ERROR_ok: _t = QMessageBox(QMessageBox.Critical, "Error #%s"%error,"Unable to send message to #%s!"%toID);_t.show();return
        elif targetMode == ts3defines.TextMessageTargetMode.TextMessageTarget_CLIENT:
            for msg in message:
                error = ts3lib.requestSendPrivateTextMsg(schid, "\n"+msg, toID)
                if not error == ts3defines.ERROR_ok: _t = QMessageBox(QMessageBox.Critical, "Error #%s"%error,"Unable to send message to #%s!"%toID);_t.show();return
