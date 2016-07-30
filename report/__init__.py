import ts3lib as ts3; from ts3plugin import ts3plugin, PluginHost
from pytsonui import setupUi
from PythonQt.QtGui import QDialog, QListWidgetItem, QWidget, QListWidget
from PythonQt.QtCore import Qt
import ts3lib as ts3; import   ts3defines, datetime, os

class report(ts3plugin):
    name = "Report"
    import pytson;apiVersion = pytson.getCurrentApiVersion()
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Gives you the ability to quickly Report Users to Moderators.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = ""
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Add to Moderator", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 1, "Remove from Moderators", ""),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 2, "Report User", "")]
    hotkeys = []
    debug = False


    def __init__(self):
        ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/Bluscream]Bluscream[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if menuItemID == 0:
            schid = ts3.getCurrentServerConnectionHandlerID()
            (error, item) = ts3.getClientDisplayName(schid, selectedItemID)
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.datetime.now())+" [color=green]Added[/color] [color=yellow]"+item+"[/color] to Report Moderators.")
        if menuItemID == 1:
            schid = ts3.getCurrentServerConnectionHandlerID()
            (error, item) = ts3.getClientDisplayName(schid, selectedItemID)
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.datetime.now())+" [color=red]Removed[/color] [color=yellow]"+item+"[/color] from Report Moderators.")
        if menuItemID == 2:
            self.dlg = ReportDialog(None)
            self.dlg.show()


class ReportDialog(QDialog):
    #[(objectName, store, [children])]
    CONF_REASONS = ["Hacker", "DDoS Threat", "Test"]
    CONF_WIDGETS = [("reasons", True, []),("customreason", True, []),("submit", True, [])]

    def __init__(self, parent):
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "ressources", "report.ui"), self.CONF_WIDGETS)
        self.setupList()

        self.reasons.connect("currentItemChanged(QListWidgetItem*, QListWidgetItem*)", self.onReasonListCurrentItemChanged)
        #self.reasons.connect("itemChanged(QListWidgetItem*)", self.onReasonListItemChanged)


    def setupList(self):
        #self.reasons.clear()
        #_list = QListWidget(self.reasons)
        for reason in self.CONF_REASONS:
            item = QListWidgetItem(self.reasons)
            item.setText(reason)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            #item.setCheckState(Qt.Unchecked)
            #item.setData(Qt.UserRole, reason)
            #self.reasons.sortItems()


    def onReasonListCurrentItemChanged(self, item):
        #checked = item.checkState() == Qt.Checked
        #name = item.data(Qt.UserRole)

    #if checked and name not in self.host.active:
        #self.host.activate(name)
    #elif not checked and name in self.host.active:
        #self.host.deactivate(name)

        #if self.pluginsList.currentItem() == item:
        self.customreason.setText(self.reasons.currentRow())

    def on_submit_clicked(self):
        schid = ts3.getCurrentServerConnectionHandlerID()
        ts3.requestSendPrivateTextMsg(schid, "Reported", 0)
