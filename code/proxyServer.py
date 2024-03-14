import socket
import select
from threading import Thread
import re
import time

HOST = '127.0.0.1'
PORT = 8080
BUFFER_SIZE = 1024
BACKLOG = 10


class Server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.Socket = None

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

    def validateMessage(self):
        return True

    def sendMessage(self, msg: bytes) -> bool:
        if not self.validateMessage():
            return False
        try:
            self.Socket.send(msg)
        except ConnectionRefusedError:
            self.closeConnection()
            print(f"** Server {self.host} crashed **")
            return False
        return True

    def reciveAnswer(self) -> bytes:
        answer = self.Socket.recv(BUFFER_SIZE)
        print("Got response from server")
        return answer

    def handleRequest(self, request: bytes):
        if not self.sendMessage(request):
            return 'Error'
        rsp = self.reciveAnswer()
        return rsp


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


def initServers(communicationList: dict[Server:list[Client]] = {}) -> list[Server]:
    continueAsking = True
    while continueAsking:
        serverProps = input("Enter 1 or more servers' IPs and ports (i.e. 127.0.0.1, 12345): ")
        serverProps = checkServerProps(serverProps)
        for host, port in serverProps:
            server = Server(host, int(port))
            communicationList[server] = []
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


def lookForClients(communicationList: dict[Server:list[Client]], proxySocket: socket.socket):
    communicationList = dict()
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


def interrupt():
    while True:
        seconds = input()
        if checkInterrupt:
            seconds = seconds[1:]
            print(f"Sleeping... {seconds}sec")
            time.sleep(int(seconds))
            print("finished")


def checkInterrupt(inpt: str) -> bool:
    checkForTime = re.match("^s\d+$", inpt)
    return bool(checkForTime)


def chooseServer(serverList: list[Server]) -> Server:
    return serverList[0]


def getNewClient(communicationList: dict[Server:list[Client]], proxySocket: socket.socket, chosenServer: Server):
    clientSocket, clientAddress = proxySocket.accept()
    newClient = Client(*clientAddress, clientSocket)

    communicationList[chosenServer].append(newClient)


def runProxy():
    communicationList = initServers()
    while not communicationList:
        print("No servers were chosen, please try again")
        communicationList = initServers()
    proxySocket = initProxy()

    proxySocket.listen(BACKLOG)
    print(f"Server listening on port {PORT}...")

    lookForClientsThread = Thread(target=lookForClients, args=(communicationList, proxySocket,))
    interruptThread = Thread(target=interrupt)

    lookForClientsThread.start()
    interruptThread.start()


def main():
    runProxy()


if __name__ == "__main__":
    main()
