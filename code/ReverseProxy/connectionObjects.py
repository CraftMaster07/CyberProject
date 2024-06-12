# server.py

import socket
import select
from threading import Thread
import logging
import time


BUFFER_SIZE = 1024
ERROR = "error"
TIME_FORMAT = "%Y.%m.%d %H:%M:%S"

logger = logging.getLogger(__name__)

class BaseConnection:
    def __init__(self, host: str, port: int, type: str = "Abstract"):
        self.host: str = host
        self.port: int = port
        self.name: tuple[str, int] = (self.host, self.port)
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.initTime: int = int(time.time())
        self.type: str = type

    def connectToServer(self):
        self.socket.connect((self.host, self.port))
        logger.debug(f"Connected to {self.type} {self.name}")

    def closeConnection(self):
        self.socket.close()
        logger.debug(f"Ended Connection with {self.type} {self.name}")

    def sendData(self, data: bytes):
        try:
            self.socket.sendall(data)
        except ConnectionError:
            return ERROR

    def reciveData(self) -> bytes:
        try:
            answer = self.socket.recv(BUFFER_SIZE)
        except ConnectionError:
            return ERROR
        return answer

    def getTime(self) -> int:
        return time.strftime(TIME_FORMAT, time.localtime())


class Server(BaseConnection):
    def __init__(self, host: str, port: int, clientCount: int = 0, lastRequestTime: int = 0, lastCrashTime: int = 0):
        super().__init__(host, port, "Server")
        self.clientList: list[Client] = []
        self.thread: Thread = Thread(target=self.lookForClients)
        self.runThread: bool = True  # stopping thread if set to false
        self.clientCount: int = clientCount
        self.lastRequestTime: int = lastRequestTime
        self.lastCrashTime: int = lastCrashTime
        self.lastCheckedTime: int = int(time.time())

    def connectToServer(self) -> bool:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            super().connectToServer()
            return True
        except (ConnectionRefusedError, TimeoutError) as e:
            self.closeConnection()
            logger.error(f"** Server {self.name} Crashed **")
            logger.debug(e)
            self.lastCrashTime = self.getTime()
            return False
    
    def startThread(self):
        if not self.thread.is_alive():
            self.thread.start()

    def lookForClients(self):
        emptySocket = socket.socket()
        while self.runThread:
            sockList = [client.socket for client in self.clientList]
            readList, _, _ = select.select([emptySocket] + sockList, [], [], 1)
            if not readList:
                continue

            for sock in readList:
                if not self.connectToServer():
                    self.runThread = False
                    break
                client = next((client for client in self.clientList if client.socket is sock), False)
                if not client:
                    continue
                self.handleRequest(client)
                client.closeConnection()
                self.removeClient(client)
                self.closeConnection()

    def sendRequest(self, msg: bytes) -> bool:
        try:
            super().sendData(msg)
            self.clientCount += 1
            self.lastRequestTime = self.getTime()
        except (ConnectionError, OSError) as e:
            self.closeConnection()
            logger.error(f"** Server {self.name} Crashed on Request Attempt **")
            logger.debug(e)
            self.lastCrashTime = self.getTime()
            return False
        return True

    def reciveResponse(self) -> bytes:
        answer = b''
        while True:
            try:
                chunk = super().reciveData()
            except ConnectionError:
                return ERROR
            if not chunk or chunk == ERROR:
                break
            answer += chunk
        logger.debug(f"Got Response from Server {self.name}")
        return answer

    def handleRequest(self, client):
        client: Client
        req: bytes = client.reciveData()
        self.lastRequestTime = self.getTime()
        if req == ERROR:
            return
        if not self.sendRequest(req):
            return
        rsp = self.reciveResponse()
        if rsp == ERROR:
            return
        client.sendData(rsp)
    
    def insertClient(self, newClient):
        self.clientList.append(newClient)
    
    def removeClient(self, newClient):
        try:
            self.clientList.remove(newClient)
        except ValueError:
            pass



class Client(BaseConnection):
    def __init__(self, host: str, port: int, Socket: socket.socket):
        super().__init__(host, port, "Client")
        self.socket = Socket