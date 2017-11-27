import pytson, ts3lib, ts3defines, itertools, re, textwrap
from ts3plugin import ts3plugin
from datetime import datetime
from collections import defaultdict

def take(n, iterable):
    """Return first n items of the iterable as a list"""
    return list(itertools.islice(iterable, n))

def date(): return '{:%Y-%m-%d}'.format(datetime.datetime.now())
def time(): return '{:%H:%M:%S}'.format(datetime.datetime.now())

def channelURL(schid=None, cid=0, name=None):
    if schid == None:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if name == None:
        try: (error, name) = ts3lib.getChannelVariable(schid, cid, ts3defines.ChannelProperties.CHANNEL_NAME)
        except: name = cid
    return '[b][url=channelid://{0}]"{1}"[/url][/b]'.format(cid, name)
def clientURL(schid=None, clid=0, uid=None, nickname=None):
    if schid == None:
        try: schid = ts3lib.getCurrentServerConnectionHandlerID()
        except: pass
    if uid == None:
        try: (error, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        except: pass
    if nickname == None:
        try: (error, nickname) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_NICKNAME)
        except: nickname = uid
    return '[url=client://{0}/{1}]{2}[/url]'.format(clid, uid, nickname)

class pingHighScore(ts3plugin):
    name = "Ping High Score"
    apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = "score"
    infoTitle = None
    menuItems = []
    hotkeys = []
    debug = False
    c = []

    @staticmethod
    def timestamp(): return '[{:%Y-%m-%d %H:%M:%S}] '.format(datetime.now())

    def __init__(self):
        if self.debug: ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(self.timestamp(),self.name,self.author))

    def processCommand(self, schid, cmd):
        cmd = cmd.split(' ', 1)
        command = cmd[0].lower()
        if command == "ping":
            count = int(cmd[1]) if cmd[1] else 5
            c = {}
            (err, clids) = ts3lib.getClientList(schid)
            for clid in clids:
                # if len(self.c) > 10: break
                if not clid in self.c:
                    ts3lib.requestConnectionInfo(schid, clid)
                    self.c.append(clid)
                (err, ping) = ts3lib.getConnectionVariableAsUInt64(schid, clid, ts3defines.ConnectionProperties.CONNECTION_PING)
                if err == ts3defines.ERROR_ok: c[clid] = ping
            print(c)
            s = sorted(c.items(), key=lambda x: int(x[1]))
            t = take(count, s)
            string = ""
            place = 1
            for k,v in t:
                string += '{0}: {1} with [b]{2}[/b]ms\n'.format(place,clientURL(schid,k),v)
                place += 1
            (err, ownid) = ts3lib.getClientID(schid)
            (err, ownchan) = ts3lib.getChannelOfClient(schid, ownid)
            message = [string[i:i + 900] for i in range(0, len(string), 900)]
            # message = re.findall('.{1,1024}(?:\n|$)', string)
            # message = (textwrap.wrap(string, 1024))
            # message = (line.strip() for line in re.findall(r'.{1,80}(?:\s+|$)', string))
            # message = textwrap.wrap(string, 1024, break_long_words=False)
            for msg in message: ts3lib.requestSendChannelTextMsg(schid, '\n{0}'.format(msg), ownchan)
        elif command == "clear":
            self.c = []
        return 1