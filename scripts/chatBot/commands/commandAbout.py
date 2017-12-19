import ts3lib
cmdpy = path.join(pytson.getPluginPath(), "scripts", "chatBot")
syspath.insert(0, cmdpy)
import chatBot as self
import chatCommand

class commandAbout(chatCommand):
    name = "time"
    version = 1
    requestAutoload = False

    def __init__(schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, "%s v%s by %s" % (self.name, self.version, self.author))