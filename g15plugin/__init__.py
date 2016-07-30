#if you wanna use this, you'll need the g15daemon module and ressources (font) from https://github.com/pathmann/g15mediadaemon; g15daemon has additional dependencies: freetype
import ts3lib as ts3
from ts3plugin import ts3plugin
import os, sys
import ts3defines

PIXEL_ON = chr(1)
MAX_X=160
"""Maximum x axis resolution"""
MAX_Y=43

if sys.platform == 'linux':
    class g15plugin(ts3plugin):
        name = "g15"
        requestAutoload = False
        version = "1.0"
        import pytson;apiVersion = pytson.getCurrentApiVersion()
        author = "Thomas \"PLuS\" Pathmann"
        description = "Display information on the g15 connected to g15daemon"
        offersConfigure = False
        commandKeyword = ""
        infoTitle = None
        menuItems = []
        hotkeys = []

        def __init__(self):
            import g15daemon
            self.g15 = g15daemon.g15screen(g15daemon.SCREEN_PIXEL)
            self.talkerids = []
            self.talkernames = []

            (err, aid) = self.g15.ttf_load(bytes(os.path.join(ts3.getPluginPath(), "pyTSon", "ressources", "unifont.ttf"), 'utf-8'), 12)

            if aid != -1:
                self.ttf_id = aid
            else:
                print("Error loading font: %s" % err)
                self.ttf_id = -1

            self.updateDisplay()

        def stop(self):
            del(self.g15)

        def updateDisplay(self):
            self.g15.clear()
            schid = ts3.getCurrentServerConnectionHandlerID()
            (err, myid) = ts3.getClientID(schid) if schid > 0 else (0, 0)
            if err == ts3defines.ERROR_ok:
                (err, chan) = ts3.getChannelOfClient(schid, myid) if myid > 0 else (0, 0)
                if err == ts3defines.ERROR_ok:
                    (err, channame) = ts3.getChannelVariableAsString(schid, chan, ts3defines.ChannelProperties.CHANNEL_NAME) if chan > 0 else (0, "TS3")
                    if err == ts3defines.ERROR_ok:
                        title = "[%s]" % channame
                        (err, away) = ts3.getClientSelfVariableAsInt(schid, ts3defines.ClientPropertiesRare.CLIENT_AWAY)
                        if err == ts3defines.ERROR_ok and away:
                            title += " Away"
                        (err1, inmute) = ts3.getClientSelfVariableAsInt(schid, ts3defines.ClientProperties.CLIENT_INPUT_MUTED)
                        (err2, outmute) = ts3.getClientSelfVariableAsInt(schid, ts3defines.ClientProperties.CLIENT_OUTPUT_MUTED)
                        if (inmute + outmute) >= 1:
                            title += " Mute:"
                            if err1 == ts3defines.ERROR_ok and inmute:
                                title += " in"
                            if err2 == ts3defines.ERROR_ok and outmute:
                                title += " out"

                        self.render_string(title, 0)
                        for i, name in enumerate(self.talkernames):
                            self.render_string(name, i +1)
                            #self.g15.render_string(name, i +1, g15daemon.G15_TEXT_LARGE, 0, 0)
                        self.g15.display()
                        return

            self.g15.render_string("TS3 ERROR!", 0, g15daemon.G15_TEXT_LARGE, 0, 0)
            self.g15.display()

        def render_string(self, string, row):
            x = 0
            if row >= 5:
                x = 80
                row -= 5

            y = row * 12

            if self.ttf_id != -1:
                self.g15.ttf_print(x, y, 12, self.ttf_id, PIXEL_ON, 0, string)
            else:
                self.g15.render_string(string, row, g15daemon.G15_TEXT_LARGE, 0, 0)

        def onClientSelfVariableUpdateEvent(self, serverConnectionHandlerID, flag, oldval, newval):
            if flag in [ts3defines.ClientProperties.CLIENT_INPUT_MUTED, ts3defines.ClientProperties.CLIENT_OUTPUT_MUTED, ts3defines.ClientPropertiesRare.CLIENT_AWAY]:
                self.updateDisplay()

        def onTalkStatusChangeEvent(self, serverConnectionHandlerID, status, isReceivedWhisper, clientID):
            if status == ts3defines.TalkStatus.STATUS_TALKING:
                if (serverConnectionHandlerID, clientID) in self.talkerids:
                    return
                (err, name) = ts3.getClientVariableAsString(serverConnectionHandlerID, clientID, ts3defines.ClientProperties.CLIENT_NICKNAME)
                if err == ts3defines.ERROR_ok:
                    self.talkerids.append((serverConnectionHandlerID, clientID))
                    self.talkernames.append(name)


            elif status == ts3defines.TalkStatus.STATUS_NOT_TALKING:
                if (serverConnectionHandlerID, clientID) not in self.talkerids:
                    return

                self.talkernames.pop(self.talkerids.index((serverConnectionHandlerID, clientID)))
                self.talkerids.remove((serverConnectionHandlerID, clientID))
            else:
                return

            self.updateDisplay()

        def onConnectStatusChangeEvent(self, schid, status, errorNumber):
            self.updateDisplay()
