import websockets

class QuarkusSocketSignaling:
    _socket: any
    _protocol: any
    _username: any
    def __init__(self, protocol, host, port, username):
        self._protocol = protocol
        self._host = host
        self._port = port
        self._username = username
        self._socket = None

    async def connect(self):
        pass

    async def _connect(self):
        if self._socket is not None:
            return
        else:
            signaling_url = "{}://{}:{}/chat/{}".format(self._protocol, self._host, self._port, self._username)
            self._socket = await websockets.connect(uri=signaling_url)

    async def close(self):
        if self._socket is not None:
            await self._socket.close()
            self._socket = None

    async def receive(self):
        await self._connect()
        data = await self._socket.recv()
        return data

    async def send(self, message):
        await self._connect()
        await self._socket.send(message)