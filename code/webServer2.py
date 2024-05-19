import socket

S_HOST = '127.0.0.1'
S_PORT = 33333
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


HTTP_RESPONSE = """\
HTTP/1.1 200 OK

<!DOCTYPE html>
<html>
<head>
    <title>XSS Vulnerable Page</title>
</head>
<body>
    <h1>Welcome to Our Website!</h1>
    <p>Please enter your name:</p>
    <form>
        <input type="text" id="nameInput">
        <button type="button" onclick="displayGreeting()">Submit</button>
    </form>
    <div id="greeting"></div>

    <script>
        function displayGreeting() {
            var name = document.getElementById('nameInput').value;
            var greeting = "Hello, " + name + "!";
            document.getElementById('greeting').innerHTML = greeting;
        }
    </script>
</body>
</html>

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
