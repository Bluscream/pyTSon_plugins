import sys
print(sys.path)
sys.path = ['C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/scripts', 'C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/include', 'C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/lib', 'C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/lib/lib-dynload', 'C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/lib/site-packages']
print(sys.path)
from PythonQt.QtNetwork import QLocalSocket
class ipcclient(object):
    class funcs(object):
        def __init__(self, path):
            self.socket = QLocalSocket()

            self.socket.connectToServer(path)

            if not self.socket.waitForConnected(1000):
                raise Exception("Error connecting to socket on %s" % path)
            else:
                self.socket.write(b"f")
                if not self.socket.waitForBytesWritten(1000):
                    raise Exception("Error registering as function socket")

        def function(self, name, *args):
            if self.socket.state() != QLocalSocket.ConnectedState:
                raise Exception("Socket is not connected")

            data = ipcdata(obj=name)

            for p in args:
                data.append(p)

            self.incmd = True
            self.socket.write((len(data.data) + ipcdata.longlen).to_bytes(ipcdata.longlen, byteorder='big') + data.data)
            if self.socket.waitForBytesWritten(1000):
                r = 0
                plen = 0

                while r < 3:
                    r += 1
                    if self.socket.waitForReadyRead(5000):
                        if plen == 0:
                            if self.socket.bytesAvailable() < ipcdata.longlen:
                                continue
                            else:
                                plen = int.from_bytes(self.socket.read(ipcdata.longlen), byteorder='big')

                        if plen != 0:
                            if plen - ipcdata.longlen != self.socket.bytesAvailable():
                                continue
                            else:
                                data = ipcdata(init=self.socket.read(self.socket.bytesAvailable()))
                                self.incmd = False
                                return data.read()
                    else:
                        self.incmd = False
                        raise Exception("Socket timed out waiting for answer")

                raise Exception("Socket timed out running 3 rounds waiting for answer")
            else:
                self.incmd = False
                raise Exception("Socket timed out during write process")

        def __getattr__(self, name):
            return (lambda *args: self.function(name, *args))

    def __init__(self, path):
        self.incmd = False

        self.buf = bytes()

        self.socket = QLocalSocket()
        self.socket.readyRead.connect(self.onReadyRead)

        self._funcs = ipcclient.funcs(path)

        self.socket.connectToServer(path)

        if not self.socket.waitForConnected(1000):
            raise Exception("Error connecting to socket on %s" % path)
        else:
            self.socket.write(b"c")
            if not self.socket.waitForBytesWritten(1000):
                    raise Exception("Error registering as callback socket")

    def onReadyRead(self):
        if self.incmd:
            return

        self.buf += self.socket.read(self.socket.bytesAvailable())
        self.handleBuffer()

    def handleBuffer(self):
        if len(self.buf) < ipcdata.longlen:
            return

        plen = int.from_bytes(self.buf[:ipcdata.longlen], byteorder='big')
        if len(self.buf) < plen: #message not complete
            return
        elif len(self.buf) > plen: #multiple messages
            self.handleCallback(self.buf[ipcdata.longlen:plen])
            self.buf = self.buf[plen:]
            self.handleBuffer()
        else: #only one message len(self.buf) == plen
            self.handleCallback(self.buf[ipcdata.longlen:])
            self.buf = bytes()

    def handleCallback(self, buf):
        data = ipcdata(init=buf)
        name = data.read()

        if hasattr(self, name):
            getattr(self, name)(*tuple(data.readAll()))

    @property
    def functions(self):
        return self._funcs

class myclient(ipcclient):
    def onTalkStatusChangeEvent(self, serverConnectionHandlerID, status, isReceivedWhisper, clientID):
        print("talkstatus %s %s %s" % (serverConnectionHandlerID, status, clientID))

    def onClientSelfVariableUpdateEvent(self, schid, flag, oldval, newval):
        print("selfupdate %s %s %s %s" % (schid, flag, oldval, newval))

client = myclient("C:/Users/blusc/AppData/Roaming/TS3Client/plugins/pyTSon/ipcsocket")
#get client id of schid=1
(err, myid) = client.functions.getClientID(1)
print(myid)
