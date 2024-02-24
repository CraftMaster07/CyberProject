import socket
from threading import Thread
import sys

HOST = '127.0.0.1'
S_HOST = '127.0.0.1'
PORT = 8080
S_PORT = 25565
BUFFER_SIZE = 1024
BACKLOG = 10


def initProxy():
    proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxySocket.bind((HOST, PORT))
    print("Proxy is up and running!")

    return proxySocket


def connectToServer(host, port):
    newServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    newServerSocket.connect((host, port))
    print("Connected to a server")
    return newServerSocket


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


def handleClient(proxySocket, serverSockets):
    clientSocket, clientAddress = proxySocket.accept()
    with clientSocket as clientSock:
        clientAddress = clientAddress
        req = getRequest(clientSock)
        sendMessage(serverSockets[0], req)
        rsp = getResponse(serverSockets[0])
        sendMessage(clientSock, rsp)



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