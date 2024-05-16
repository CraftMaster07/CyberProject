import socket
import psutil
import os

S_HOST = '127.0.0.1'
S_PORT = 12345
BUFFER_SIZE = 1024
BACKLOG = 10
DIRECTORY = "code/happybirthday"
DIRECTORY = "twoFiles"

HTTP_RESPONSE = """\
HTTP/1.1 200 OK

<!DOCTYPE html>
<html>
<head>
<title>Page Title</title>
</head>
<body>

<h1>My First Heading</h1>
<p>My first paragraph.</p>

</body>
</html>
"""

def initServer():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((S_HOST, S_PORT))
    print("Server is up and running!")

    return serverSocket


def findSourceRequested(requestHeader: str) -> str:
    RequestedFilePath = requestHeader.split(" ")[1]
    if RequestedFilePath == '/':
        return "/index.html"
    return RequestedFilePath


def getContentType(request):
    request = request.split('\n')
    header = next((line for line in request if line.startswith('Accept:')), None)
    if header:
        contentType = header.split(':')[1].strip().split(',')
        return contentType[0].strip()
    return 'text/plain'


def handleRequest(clientSocket: socket.socket):
    try:
        request = clientSocket.recv(BUFFER_SIZE).decode()
    except ConnectionResetError:
        clientSocket.close()
        return

    print("Request:")
    print(request)
    response = directoryResponse(request)
    '''
    with open("code\index.html", 'r') as file:
        response = file.read()
    response = (
        "HTTP/1.1 200 OK\r\n\r\n"
        f"{response}"
    )
    '''
    clientSocket.sendall(response.encode())
    clientSocket.close()


def directoryResponse(request: str) -> str:
    requestt = request.split("\r\n")
    reqFilePath = findSourceRequested(requestt[0])

    try:
        with open(f"{DIRECTORY}{reqFilePath}", 'r') as file:
            response = file.read()
    except UnicodeDecodeError:
        with open(f"{DIRECTORY}{reqFilePath}", 'rb') as file:
            response = file.read()

    contentType = getContentType(request)
    if "image/avif" in contentType:
        contentType = contentType[:-4] + reqFilePath.split(".")[1]
        contentType += f"\r\nContent-Length: {len(response)}"

    response = (
        "HTTP/1.1 200 OK\r\n"
        f"Content-Type: {contentType}\r\n\r\n"
        f"{response}"
    )
    return response


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
