import ts3lib
cmdpy = path.join(pytson.getPluginPath(), "scripts", "chatBot")
syspath.insert(0, cmdpy)
import chatBot as self

class commandAbout(chatCommand):
    name = "about"
    version = 1
    requestAutoload = False

    def __init__(schid, targetMode, toID, fromID, params=""):
        self.answerMessage(schid, targetMode, toID, fromID, 'My current time is: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))