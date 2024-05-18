import socket
from threading import Thread

HOST = '0.0.0.0'
PORT = 11111
BUFFER_SIZE = 1024
BACKLOG = 10

HTTP_RESPONSE = """\
HTTP/1.1 200 OK

RESPONSE
"""


def initServer():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((HOST, PORT))
    print("Server is up and running!")

    return serverSocket


def handleRequest(clientSocket):
    request = clientSocket.recv(BUFFER_SIZE).decode()
    print("Request:")
    print(request)

    response = HTTP_RESPONSE
    clientSocket.sendall(response.encode())
    clientSocket.close()


def runServer():
    serverSocket = initServer()
    serverSocket.listen(BACKLOG)
    print(f"Server listening on port {PORT}...")

    while True:
        clientSocket, clientAddress = serverSocket.accept()
        handleRequest(clientSocket)


def main():
    runServer()


if __name__ == "__main__":
    main()