import ts3lib
cmdpy = path.join(pytson.getPluginPath(), "scripts", "chatBot")
syspath.insert(0, cmdpy)
import chatBot as self

class commandAbout(chatCommand):
    name = "about"
    version = 1
    requestAutoload = True

    def __init__(schid, targetMode, toID, fromID, params=""):
        try:
            eval(params)
        except TypeError as e:
            if e.strerror == "eval() arg 1 must be a string, bytes or code object": pass
            else:
                from traceback import format_exc;self.answerMessage(schid, targetMode, toID, fromID, format_exc())
        except:
            from traceback import format_exc;self.answerMessage(schid, targetMode, toID, fromID, format_exc())