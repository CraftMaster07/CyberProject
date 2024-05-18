import socket
import json
import sqlite3


HOST = '127.0.0.1'
PORT = 12344
FILE_PATH = "code/gptServerWithPostDelete/"

# Initialize SQLite database
conn = sqlite3.connect(f'{FILE_PATH}items.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
''')
conn.commit()
conn.close()  # Close the connection after creating the table

# Function to read HTML content from file
def read_html_file():
    with open(f'{FILE_PATH}index.html', 'r') as file:
        return file.read()

# Function to generate HTML response
def generate_html_response():
    html_content = read_html_file()
    response_headers = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
    return response_headers + html_content

# Function to handle POST requests
def handle_post_request(request_body):
    try:
        data = json.loads(request_body)
        item_name = data.get('name', '')
        if not item_name:
            return 'Item name is required', 400

        conn = sqlite3.connect(f'{FILE_PATH}items.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO items (name) VALUES (?)', (item_name,))
        conn.commit()
        conn.close()

        response_body = json.dumps({'id': cursor.lastrowid, 'name': item_name})
        return response_body, 201
    except Exception as e:
        return str(e), 500

# Function to handle DELETE requests
def handle_delete_request(request_path):
    try:
        item_id = int(request_path.split('/')[-1])
        conn = sqlite3.connect(f'{FILE_PATH}items.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()

        return '', 204
    except Exception as e:
        return str(e), 500

# Main function to handle HTTP requests
def handle_request(request):
    try:
        request_lines = request.split('\r\n')
        method, path, _ = request_lines[0].split(' ')

        if path == '/':
            return generate_html_response(), 200
        elif method == 'POST':
            content_length = int([line.split(': ')[1] for line in request_lines if 'Content-Length' in line][0])
            request_body = request_lines[-1]
            return handle_post_request(request_body)
        elif method == 'DELETE':
            return handle_delete_request(path)
        else:
            return 'Method not allowed', 405
    except Exception as e:
        return str(e), 500

# Main server loop
def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f'Server listening on http://{HOST}:{PORT}')

    while True:
        client_socket, client_address = server_socket.accept()
        request = client_socket.recv(4096).decode('utf-8')

        response_body, status_code = handle_request(request)
        client_socket.sendall(response_body.encode('utf-8'))
        client_socket.close()

if __name__ == '__main__':
    run_server()
