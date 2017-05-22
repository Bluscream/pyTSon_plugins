import ts3lib as ts3; from ts3plugin import ts3plugin, PluginHost
import ts3lib as ts3; import   ts3defines, datetime, configparser, os.path
from PythonQt.QtGui import QDialog, QInputDialog, QMessageBox

class profile(ts3plugin):
    name = "Profile"
    try: apiVersion = pytson.getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = "Share your info\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = True
    commandKeyword = ""
    infoTitle = "[b]"+name+":[/b]"
    menuItems = []
    hotkeys = []
    ini = os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "profile", "cfg", "profile.ini")
    config = configparser.ConfigParser()
    META_START = '<profile>'
    META_DIVIDER = '##$#'
    META_COLON = '§$#'
    META_STOP = '</profile>'

    def __init__(self):
        if os.path.isfile(self.ini):
            self.config.read(self.ini)
        else:
            self.config['GENERAL'] = { "Debug": "False" }
            self.config['PROFILE'] = { "Test": "[url=https://google.com]Google[/url]"}
            with open(self.ini, 'w') as configfile:
                self.config.write(configfile)
        ts3.logMessage(self.name+" script for pyTSon by "+self.author+" loaded from \""+__file__+"\".", ts3defines.LogLevel.LogLevel_INFO, "Python Script", 0)
        if self.config['GENERAL']['Debug'] == "True":
            ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/"+self.author+"]"+self.author+"[/url] loaded.")

    def configure(self, qParentWidget):
        if not self.dlg:
            self.dlg = MainWindow(self)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

    def infoData(self, schid, id, atype):
        schid = ts3.getCurrentServerConnectionHandlerID()
        if atype == 2:
            (error, meta) = ts3.getClientVariableAsString(schid, id, ts3defines.ClientProperties.CLIENT_META_DATA)
            if error == ts3defines.ERROR_ok and meta != "" and self.META_START in meta and self.META_STOP in meta:
                _tmp = ""; meta = meta.split(self.META_START)[1];meta = meta.split(self.META_STOP)[0];meta = meta.split(self.META_DIVIDER)
                for item in meta:
                    item = item.split(self.META_COLON)
                    ts3.printMessageToCurrentTab("item: "+str(item))
                    _tmp += item[0]+": "+item[1]
                if not _tmp == "":
                    return _tmp.replace("\n", "").replace("\r", "")

class MainWindow(QDialog):
    def __init__(self,cfg, parent=None):
        self.cfg=cfg
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "profile", "ui", "profile.ui"))
        self.setWindowTitle("Set up profile")
