import socket

def main():
    # HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Example Page</title>
        <link rel="stylesheet" href="styles.css"> <!-- Include CSS file -->
    </head>
    <body>
        <h1>Hello, world!</h1>
        <p>This is an example webpage.</p>
    </body>
    </html>
    """

    # CSS content
    css_content = """
    h1 {
        color: yellow;
    }
    """

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

        

        # Send HTTP response with CSS content
        css_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/css\r\n\r\n"
            f"{css_content}"
        )
        client_socket.sendall(css_response.encode())

        # Send HTTP response with HTML content
        html_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n\r\n"
            f"{html_content}"
        )
        client_socket.sendall(html_response.encode())

        # Close the connection
        client_socket.close()

if __name__ == "__main__":
    main()
