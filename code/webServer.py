import socket
from threading import Thread
import psutil

S_HOST = '127.0.0.1'
S_PORT = 8080
BUFFER_SIZE = 1024
BACKLOG = 10

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

HTTP_WITH_CSS_RESPONSE = """\
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Example Page</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>Hello, world!</h1>
    <p>This is an example webpage.</p>
</body>
</html>"""

HTTP_WITH_CSS_RESPONSE2 = """\
HTTP/1.1 200 OK
Content-Type: text/css

body {
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
}

h1 {
    color: green;
}
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

    with open("happybirthday/index.html",'r') as file:
        response = file.read()
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

