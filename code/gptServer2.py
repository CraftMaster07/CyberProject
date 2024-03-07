import socket
import os

def serve_html_file(file_path):
    try:
        # Read HTML file
        with open(file_path, "r") as file:
            html_content = file.read()
        return html_content
    except FileNotFoundError:
        return "HTTP/1.1 404 Not Found\r\n\r\n404 Not Found: The requested file was not found."

def main():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a host and port
    server_address = ('localhost', 8080)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)
    print("Server listening on port 8080...")

    while True:
        # Wait for a connection
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        # Serve the HTML page
        html_response = serve_html_file("happybirthday/index.html")

        # Send HTTP response
        client_socket.sendall(html_response.encode())

        # Close the connection
        client_socket.close()

if __name__ == "__main__":
    main()