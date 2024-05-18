import socket
import select
from threading import Thread
import re
import bleach
import random
import logging
import time


HOST = '0.0.0.0'
PORT = 8080
BUFFER_SIZE = 1024
BACKLOG = 10
ERROR = "error"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(asctime)s]%(levelname)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

fileHandler = logging.FileHandler('sample.log')
fileHandler.setLevel(logging.CRITICAL)
fileHandler.setFormatter(formatter)

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

class Server:
    def __init__(self, host: str, port: int):
        self.host: str = host
        self.port: int = port
        self.name: list[str, int] = (self.host, self.port)
        self.Socket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientList: list[Client] = []
        self.Thread: Thread = Thread(target=self.lookForClients)
        self.runThread: bool = True  # stopping thread if set to false

    def connectToServer(self) -> bool:
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.Socket.connect((self.host, self.port))
            logger.debug(f"Connected to Server {self.name}")
            return True
        except (ConnectionRefusedError, TimeoutError) as e:
            self.closeConnection()
            logger.error(f"** Server {self.name} Crashed **")
            return False

    def closeConnection(self):
        self.Socket.close()
        logger.debug(f"Ended Connection with Server {self.name}")
    
    def startThread(self):
        if not self.Thread.is_alive():
            self.Thread.start()

    def lookForClients(self):
        emptySocket = socket.socket()
        while self.runThread:
            sockList = [client.Socket for client in self.clientList]
            readList, _, _ = select.select([emptySocket] + sockList, [], [], 1)
            if not readList:
                continue

            for sock in readList:
                if not self.connectToServer():
                    self.runThread = False
                    break
                client = next((client for client in self.clientList if client.Socket is sock), False)
                if not client:
                    continue
                self.handleRequest(client)
                client.closeConnection()
                self.removeClient(client)
                self.closeConnection()

    def validateMessage(self) -> bool:
        return True

    def sendRequest(self, msg: bytes) -> bool:
        if not self.validateMessage():
            return False
        try:
            msg = sanitizeMessage(msg)
            self.Socket.sendall(msg)
        except (ConnectionError, OSError) as e:
            self.closeConnection()
            logger.error(f"** Server {self.name} crashed on request attempt **")
            return False
        return True

    def reciveResponse(self) -> bytes:
        answer = b''
        while True:
            try:
                chunk = self.Socket.recv(BUFFER_SIZE)
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
        self.name: list[str, int] = (self.host, self.port)
        self.Socket: socket.socket = Socket

    def closeConnection(self):
        self.Socket.close()
        logger.debug(f"Ended connection with client {self.name}")

    def validateMessage(self) -> bool:
        return True

    def reciveRequest(self) -> bytes:
        try:
            answer = self.Socket.recv(BUFFER_SIZE)
        except ConnectionError:
            return ERROR
        return answer

    def sendResponse(self, msg: bytes) -> bool:
        if not self.validateMessage():
            return False
        self.Socket.sendall(msg)
        return True


class LoadBalancer:
    def __init__(self):
        pass

def initProxy() -> socket.socket:
    proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxySocket.bind((HOST, PORT))
    logger.info("Proxy is up and running!")

    return proxySocket


def sendMessage(dSock: socket.socket, request: bytes):
    dSock.sendall(request)


def reciveData(sock: socket.socket) -> bytes:
    answer = b''
    while True:
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            break
        answer += chunk
    return answer


def sanitizeMessage(msg: bytes) -> bytes:
    msg = msg.decode()

    msgBody = re.search("\r\n\r\n", msg)
    if msgBody:
        bodyIndex = msgBody.span()[1]
        msgHeaders = msg[:bodyIndex]
        splitHeaders = msgHeaders.split('\r\n')

        msgBody = msg[bodyIndex:]
        msgBody = bleach.clean(msgBody)
    
    newMsg = msgHeaders + msgBody
    newMsg = newMsg.encode()
    return newMsg


def initServers(communicationList: list[Server] = []) -> list[Server]:
    continueAsking = True
    while continueAsking:
        logger.info("Enter 1 or more servers' IPs and ports (i.e. 127.0.0.1, 12345): ")
        serverProps = input()
        serverProps = checkServerProps(serverProps)
        for host, port in serverProps:
            server = Server(host, int(port))
            communicationList.append(server)
        logger.info("Add more servers? (Y/N)")
        serverProps = input()
        continueAsking = bool(re.search("[Y,y]", serverProps))
    if communicationList:
        logger.info("Server(s): " + ", ".join([str(x.name) for x in communicationList]))
        for server in communicationList:
            server.startThread()
    else:
        logger.info("No Servers were Chosen")
        serverProps = initServers(communicationList)

    return communicationList


def checkServerProps(serverProps: str) -> zip:
    serverProps = "^" + serverProps
    IPv4Format = "[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}"
    hosts = re.findall(IPv4Format, serverProps)
    for host in set(hosts):
        serverProps = serverProps.replace(host, ".")
    ports = re.findall("[^0-9][0-9]{1,5}", serverProps)
    ports = [x[1:] for x in ports]
    return zip(hosts, ports)


def lookForClients(communicationList: list[Server], proxySocket: socket.socket):
    while True:
        if not communicationList:
            communicationList = initServers()
        currentServer = chooseServer(communicationList)
        readList, _, _ = select.select([proxySocket], [], []) # need to get server status
        for sock in readList:
            if sock is proxySocket:
                getNewClient(proxySocket, currentServer)
                    


def chooseServer(serverList: list[Server]) -> Server:
    server:Server = serverList[random.randint(0,len(serverList)-1)]

    if server.runThread:
        return server
    serverList.remove(server)
    if not serverList:
        logger.warning("*** ALL SERVERS ARE DOWN, PLEASE CHOOSE NEW SERVERS ***")
        serverList.extend(initServers())
    chooseServer(serverList)


def getNewClient(proxySocket: socket.socket, chosenServer: Server):
    clientSocket, clientAddress = proxySocket.accept()
    newClient = Client(*clientAddress, clientSocket)
    logger.debug(f"New Client Joined: {newClient.name}")
    chosenServer.insertClient(newClient)


def runProxy():
    communicationList = initServers()
    proxySocket = initProxy()

    proxySocket.listen(BACKLOG)
    logger.info(f"Server listening on port {PORT}...")
    lookForClients(communicationList, proxySocket,)


def main():
    runProxy()


if __name__ == "__main__":
    main()
