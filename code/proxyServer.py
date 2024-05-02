import socket
import select
from threading import Thread
import re
import bleach
import random
import time


HOST = '127.0.0.1'
PORT = 8080
BUFFER_SIZE = 1024
BACKLOG = 10


class Server:
    def __init__(self, host: str, port: int):
        self.host: str = host
        self.port: int = port
        self.Socket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientList: list[Client] = []
        self.Thread: Thread = Thread(target=self.lookForClients)
        self.stopThread: bool = False

    def connectToServer(self) -> bool:
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.Socket.connect((self.host, self.port))
            print(f"Connected to {self.host}")
            return True
        except ConnectionRefusedError:
            self.closeConnection()
            print(f"** Server {self.host} crashed **")
            return False

    def closeConnection(self):
        self.Socket.close()
        print(f"Ended connection with server({self.host})")
    
    def startThread(self):
        if not self.Thread.is_alive():
            self.Thread.start()

    def lookForClients(self):
        emptySocket = socket.socket()
        while not self.stopThread:
            sockList = [client.Socket for client in self.clientList]
            readList, _, _ = select.select([emptySocket] + sockList, [], [], 1)
            if not readList:
                continue

            for sock in readList:
                if not self.connectToServer():
                    self.stopThread = True
                print(f"clientList: {self.clientList}")
                client = next((client for client in self.clientList if client.Socket is sock), False)
                if not client:
                    continue
                self.handleRequest(client)
                client.closeConnection()
                self.removeClient(client)
                self.closeConnection()

    def validateMessage(self):
        return True

    def sendRequest(self, msg: bytes) -> bool:
        if not self.validateMessage():
            return False
        try:
            msg = sanitizeMessage(msg)
            self.Socket.send(msg)
        except (ConnectionRefusedError, OSError) as e:
            self.closeConnection()
            print(f"** Server {self.host} crashed **")
            return False
        return True

    def reciveResponse(self) -> bytes:
        answer = self.Socket.recv(BUFFER_SIZE)
        print("Got response from server")
        return answer

    def handleRequest(self, client):
        client: Client
        req: bytes = client.reciveRequest()
        if not self.sendRequest(req):
            return
        rsp = self.reciveResponse()
        client.sendResponse(rsp)
    
    def insertClient(self, newClient):
        self.clientList.append(newClient)
    
    def removeClient(self, newClient):
        self.clientList.remove(newClient)


class Client:
    def __init__(self, host: str, port: int, Socket: socket.socket):
        self.host = host
        self.port = port
        self.Socket = Socket

    def closeConnection(self):
        self.Socket.close()
        print(f"Ended connection with client({self.host})")

    def validateMessage(self):
        return True

    def reciveRequest(self) -> bytes:
        answer = self.Socket.recv(BUFFER_SIZE)
        print("Got request from client")
        return answer

    def sendResponse(self, msg: bytes) -> bool:
        if not self.validateMessage():
            return False
        self.Socket.send(msg)
        return True


def initProxy():
    proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxySocket.bind((HOST, PORT))
    print("Proxy is up and running!")

    return proxySocket


def sendMessage(dSock: socket.socket, request: bytes):
    dSock.send(request)


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

#def parseHTTPRequest():


def getRequest(clientSocket: socket.socket) -> bytes:
    request = clientSocket.recv(BUFFER_SIZE)
    print(f"Got request from client")
    return request


def handleClient(proxySocket: socket.socket, serverList: list[Server]):
    clientSocket, clientAddress = proxySocket.accept()
    newClient = Client(*clientAddress, clientSocket)

    notFoundServer = True
    while notFoundServer:
        currentServer = chooseServer(serverList)
        if currentServer.connectToServer():
            notFoundServer = False
        else:
            serverList.remove(currentServer)

    req = newClient.reciveRequest()
    rsp = currentServer.handleRequest(req)
    newClient.sendResponse(rsp)
    newClient.closeConnection()

    currentServer.closeConnection()


def initServers(communicationList: list[Server] = []) -> list[Server]:
    continueAsking = True
    while continueAsking:
        serverProps = input("Enter 1 or more servers' IPs and ports (i.e. 127.0.0.1, 12345): ")
        serverProps = checkServerProps(serverProps)
        for host, port in serverProps:
            server = Server(host, int(port))
            communicationList.append(server)
        serverProps = input("Add more servers? (Y/N)")
        continueAsking = bool(re.search("[Y,y]", serverProps))

    for server in communicationList:
        server.startThread()
    return communicationList


def checkServerProps(serverProps: str) -> zip:
    serverProps = "^" + serverProps
    IPv4Format = "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
    hosts = re.findall(IPv4Format, serverProps)
    for host in set(hosts):
        serverProps = serverProps.replace(host, ".")
    ports = re.findall("[^0-9][0-9]{1,5}", serverProps)
    ports = [x[1:] for x in ports]
    return zip(hosts, ports)


def lookForClients(communicationList: list[Server], proxySocket: socket.socket):
    while True:
        currentServer = chooseServer(communicationList)
        readList, _, _ = select.select([proxySocket], [], []) # get server status
        for sock in readList:
            if sock is proxySocket:
                getNewClient(communicationList, proxySocket, currentServer)
                    


def chooseServer(serverList: list[Server]) -> Server:
    return serverList[random.randint(0,len(serverList)-1)]


def getNewClient(communicationList: list[Server], proxySocket: socket.socket, chosenServer: Server):
    clientSocket, clientAddress = proxySocket.accept()
    newClient = Client(*clientAddress, clientSocket)
    chosenServer.insertClient(newClient)


def runProxy():
    communicationList = initServers()
    while not communicationList:
        print("No servers were chosen, please try again")
        communicationList = initServers()
    proxySocket = initProxy()

    proxySocket.listen(BACKLOG)
    print(f"Server listening on port {PORT}...")
    lookForClients(communicationList, proxySocket,)


def main():
    runProxy()


if __name__ == "__main__":
    main()
