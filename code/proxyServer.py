import socket
import select
from threading import Thread
import re
import bleach

HOST = '127.0.0.1'
PORT = 8080
BUFFER_SIZE = 1024
BACKLOG = 10


class Server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.Socket:socket.socket = None
        self.clientList: list[Client] = []
        self.Thread: Thread = Thread(target=self.lookForClients)

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
        while True:
            sockList = [client.Socket for client in self.clientList]
            readList, _, _ = select.select([sockList], [], [])
            for sock in readList:
                if sock is proxySocket:
                    getNewClient(communicationList, proxySocket, currentServer)
                elif sock in communicationList:
                    rsp = sock.handleRequest()

    def validateMessage(self):
        return True

    def sendRequest(self, msg: bytes) -> bool:
        if not self.validateMessage():
            return False
        try:
            msg = sanitizeMessage(msg)
            self.Socket.send(msg)
        except ConnectionRefusedError:
            self.closeConnection()
            print(f"** Server {self.host} crashed **")
            return False
        return True

    def reciveResponse(self) -> bytes:
        answer = self.Socket.recv(BUFFER_SIZE)
        print("Got response from server")
        return answer

    def handleRequest(self, request: bytes):
        if not self.sendRequest(request):
            return 'Error'
        rsp = self.reciveResponse()
        return rsp
    
    def insertClient(self, newClient):
        self.clientList.insert(newClient)
    
    def removeClient(self, newClient):
        self.clientList.pop(newClient)


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
    msg = bleach.clean(msg)
    msg = msg.encode()
    return msg


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


def initServers(communicationList: list[Server] = {}) -> list[Server]:
    continueAsking = True
    while continueAsking:
        serverProps = input("Enter 1 or more servers' IPs and ports (i.e. 127.0.0.1, 12345): ")
        serverProps = checkServerProps(serverProps)
        for host, port in serverProps:
            server = Server(host, int(port))
            communicationList.append(server)
        serverProps = input("Add more servers? (Y/N)")
        continueAsking = bool(re.search("[Y,y]", serverProps))

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
        currentServer = chooseServer(communicationList.keys())
        sockList = communicationList.keys() + [clientList[0] for clientList in communicationList.values()]
        sockList = [x.Socket for x in sockList]
        readList, _, _ = select.select([proxySocket], [], [])
        for sock in readList:
            if sock is proxySocket:
                getNewClient(communicationList, proxySocket, currentServer)
            elif sock in communicationList:
                rsp = sock.handleRequest()


def chooseServer(serverList: list[Server]) -> Server:
    return serverList[0]


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

    lookForClientsThread = Thread(target=lookForClients, args=(communicationList, proxySocket,))

    lookForClientsThread.start()


def main():
    runProxy()


if __name__ == "__main__":
    main()
