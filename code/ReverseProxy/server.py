# server.py

import socket
import select
from threading import Thread
import logging
from utils import sanitizeMessage

BUFFER_SIZE = 1024
ERROR = "error"

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host: str, port: int):
        self.host: str = host
        self.port: int = port
        self.name: tuple[str, int] = (self.host, self.port)
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientList: list[Client] = []
        self.thread: Thread = Thread(target=self.lookForClients)
        self.runThread: bool = True  # stopping thread if set to false

    def connectToServer(self) -> bool:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            logger.debug(f"Connected to Server {self.name}")
            return True
        except (ConnectionRefusedError, TimeoutError) as e:
            self.closeConnection()
            logger.error(f"** Server {self.name} Crashed **")
            return False

    def closeConnection(self):
        self.socket.close()
        logger.debug(f"Ended Connection with Server {self.name}")
    
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
            msg = sanitizeMessage(msg)
            self.socket.sendall(msg)
        except (ConnectionError, OSError) as e:
            self.closeConnection()
            logger.error(f"** Server {self.name} Crashed on Request Attempt **")
            return False
        return True

    def reciveResponse(self) -> bytes:
        answer = b''
        while True:
            try:
                chunk = self.socket.recv(BUFFER_SIZE)
            except ConnectionError:
                return ERROR
            if not chunk:
                break
            answer += chunk
        logger.debug(f"Got Response from Server {self.name}")
        return answer

    def handleRequest(self, client):
        client: Client
        req: bytes = client.reciveRequest()
        if req == ERROR:
            return
        if not self.sendRequest(req):
            return
        rsp = self.reciveResponse()
        if rsp == ERROR:
            return
        client.sendResponse(rsp)
    
    def insertClient(self, newClient):
        self.clientList.append(newClient)
    
    def removeClient(self, newClient):
        try:
            self.clientList.remove(newClient)
        except ValueError:
            pass



class Client:
    def __init__(self, host: str, port: int, Socket: socket.socket):
        self.host: str = host
        self.port: int = port
        self.name: tuple[str, int] = (self.host, self.port)
        self.socket: socket.socket = Socket

    def closeConnection(self):
        self.socket.close()
        logger.debug(f"Ended connection with client {self.name}")

    def reciveRequest(self) -> bytes:
        try:
            answer = self.socket.recv(BUFFER_SIZE)
        except ConnectionError:
            return ERROR
        return answer

    def sendResponse(self, msg: bytes) -> bool:
        self.socket.sendall(msg)
        return True