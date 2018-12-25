# coding=utf-8
from ts3plugin import ts3plugin
import ts3lib, ts3defines, _ts3lib, inspect

class bookmark(ts3plugin):
    name = "Bookmark"
    requestAutoload = False
    version = "1.0"
    apiVersion = 21
    author = "Bluscream"
    description = "This is a testplugin"
    offersConfigure = False
    commandKeyword = "b"
    infoTitle = ""
    menuItems = []
    hotkeys = []
    depth = 0
    msg = ""

    def __init__(self): pass

    def processCommand(self, schid, keyword):
        keyword = keyword.lower()
        if keyword == "list":
            (err, bookmarks) = ts3lib.getBookmarkList()
            if err != ts3defines.ERROR_ok:
                ts3lib.printMessageToCurrentTab("Error: {}".format(err))
                return True
            self.msg = ""
            for bookmark in bookmarks:
                # str: name, bool: isFolder, str: uid, list<bookmark>:childs
                self.printBookmark(bookmark[0],bookmark[1],bookmark[2],bookmark[3])
            ts3lib.printMessageToCurrentTab("[color=white]{}".format(self.msg))
        return True
#┏╋━━━━━━◥◣◆◢◤━━━━━━╋┓"
#┗╋━━━━━━◥◣◆◢◤━━━━━━╋┛"
# ┣ AFK | AutoMove
    def printBookmark(self, name, isFolder, uid, childs):
        hasChilds = False
        if childs is not None: hasChilds = len(childs)
        startchar = "" # ━
        isChild = self.depth > 0
        if isChild and hasChilds: startchar = "┣"
        elif self.depth > 0: startchar = "┗"
        elif hasChilds: startchar = "┏"
        self.msg += "{}{} {}\n".format(startchar, (self.depth-1)*"━", name)
        if not isFolder: self.depth = 0
        else: # elif len(childs):
            for child in childs:
                self.depth += 1
                self.printBookmark(child[0],child[1],child[2],child[3])