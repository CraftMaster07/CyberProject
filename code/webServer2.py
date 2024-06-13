import socket
import webServer

webServer.S_HOST = '127.0.0.1'
webServer.S_PORT = 33333
webServer.BUFFER_SIZE = 1024
webServer.BACKLOG = 10
webServer.DIRECTORY = "code/happybirthday"
webServer.DIRECTORY = "server2"

webServer.HTTP_RESPONSE = """\
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


if __name__ == "__main__":
    webServer.runServer()
