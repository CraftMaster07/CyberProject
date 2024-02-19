'''import socket

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("0.0.0.0",12345))

backlog = 10
serverSocket.listen(backlog)

clientSocket, clientAddress = serverSocket.accept()
clientSocket.recv(1024)'''
import socket

HOST = '0.0.0.0'  # localhost
PORT = 8080         # Port to listen on
BUFFER_SIZE = 1024  # Buffer size for receiving data

# HTTP response template
HTTP_RESPONSE = """\
HTTP/1.1 200 OK

Hello, World!
"""

def handle_request(client_socket):
    request_data = client_socket.recv(BUFFER_SIZE).decode()
    print("Request:")
    print(request_data)

    # Send HTTP response
    client_socket.sendall(HTTP_RESPONSE.encode())
    client_socket.close()

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"Server listening on port {PORT}...")

        while True:
            client_socket, _ = server_socket.accept()
            handle_request(client_socket)

if __name__ == "__main__":
    run_server()