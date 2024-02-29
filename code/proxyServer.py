import socket
from threading import Thread
import sys

HOST = '127.0.0.1'
S_HOST = '127.0.0.1'
PORT = 8080
S_PORT = 25565
BUFFER_SIZE = 1024
BACKLOG = 10


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def connectToServer(self):
        newServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        newServerSocket.connect((self.host, self.port))
        print("Connected to a server")
        return newServerSocket


def initProxy():
    proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxySocket.bind((HOST, PORT))
    print("Proxy is up and running!")

    return proxySocket


def sendMessage(dSock, request):
    if not validateMessage():
        return False
    dSock.send(request)
    return True


def getRequest(clientSocket):
    request = clientSocket.recv(BUFFER_SIZE)
    print(f"Got request from client")
    return request

def getResponse(serverSocket):
    response = serverSocket.recv(BUFFER_SIZE)
    print(f"Got response from server")
    return response


def validateMessage():
    return True


def handleClient(proxySocket: socket.socket, serverSockets: list[socket.socket])
    clientSocket, clientAddress = proxySocket.accept()
    with clientSocket as clientSock:
        clientAddress = clientAddress
        req = getRequest(clientSock)
        sendMessage(serverSockets[0], req)
        rsp = getResponse(serverSockets[0])
        sendMessage(clientSock, rsp)


def initServers(serverList: list[tuple[str, int]]) -> list[tuple[str, int]]:
    continueAsking = True
    while continueAsking:
        serverProps: str = input("Enter server's IP and port (i.e. 127.0.0.1, 12345): ")
        serverProps: list[str] = serverProps.split(",")
        serverList.append(serverProps)
    
    return serverList



def runProxy():
    serverSockets = []
    serverSockets.append(connectToServer(S_HOST, S_PORT))

    proxySocket = initProxy()
    proxySocket.listen(BACKLOG)
    print(f"Server listening on port {PORT}...")

    while True:
        handleClient(proxySocket, serverSockets)
        serverSockets.pop()
        serverSockets.append(connectToServer(S_HOST, S_PORT))

def main():
    runProxy()

if __name__ == "__main__":
    main()
