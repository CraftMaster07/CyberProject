import socket
from threading import Thread

S_HOST = '127.0.0.1'
S_PORT = 25565
BUFFER_SIZE = 1024
BACKLOG = 10

HTTP_RESPONSE = """\
HTTP/1.1 200 OK

RESPONSE
"""


def initServer():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((S_HOST, S_PORT))
    print("Server is up and running!")

    return serverSocket


def handleRequest(clientSocket):
    try:
        request = clientSocket.recv(BUFFER_SIZE).decode()
    except ConnectionResetError:
        clientSocket.close()
        return
    
    print("Request:")
    print(request.split("\r\n"))

    response = HTTP_RESPONSE
    clientSocket.sendall(response.encode())
    clientSocket.close()


def runServer():
    serverSocket = initServer()
    serverSocket.listen(BACKLOG)
    print(f"Server listening on port {S_PORT}...")

    while True:
        clientSocket, clientAddress = serverSocket.accept()
        handleRequest(clientSocket)


def main():
    runServer()


if __name__ == "__main__":
    main()
