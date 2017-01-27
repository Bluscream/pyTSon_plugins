import ts3lib
cmdpy = path.join(ts3lib.getPluginPath(), "pyTSon", "scripts", "chatBot")
syspath.insert(0, cmdpy)
import __init__ as self
def commandAbout(schid, targetMode, toID, fromID, params=""):
    self.answerMessage(schid, targetMode, toID, fromID, "%s v%s by %s" % (self.name, self.version, self.author))

def commandTime(schid, targetMode, toID, fromID, params=""):
    self.answerMessage(schid, targetMode, toID, fromID, 'My current time is: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))

def commandEval(schid, targetMode, toID, fromID, params=""):
    try:
        eval(params)
    except TypeError as e:
        if e.strerror == "eval() arg 1 must be a string, bytes or code object": pass
        else:
            from traceback import format_exc;self.answerMessage(schid, targetMode, toID, fromID, format_exc())
    except:
        from traceback import format_exc;self.answerMessage(schid, targetMode, toID, fromID, format_exc())