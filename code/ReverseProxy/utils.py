# utils.py

import re
import bleach
import html

def sanitize_message(msg: bytes) -> bytes:
    msg_str = msg.decode('utf-8', errors='ignore')

    header_end = msg_str.find("\r\n\r\n")
    if header_end == -1:
        return msg

    header = msg_str[:header_end]
    body = msg_str[header_end + 4:]

    sanitized_body = bleach.clean(body)

    sanitized_msg = header.encode('utf-8') + b"\r\n\r\n" + sanitized_body.encode('utf-8')
    return sanitized_msg

def sanitizeMessage(message: bytes) -> bytes:
    """
    Escapes HTML special characters in the input message to prevent XSS attacks.
    
    Args:
        message (bytes): The input message to be sanitized.
    
    Returns:
        bytes: The sanitized message.
    """
    # Dictionary of HTML escape characters in bytes
    escape_chars = {
        b'&': b'&amp;',
        b'<': b'&lt;',
        b'>': b'&gt;',
        b'"': b'&quot;',
        b"'": b'&#x27;',
        b'/': b'&#x2F;',
    }
    
    sanitized_message = bytearray()
    
    for byte in message:
        sanitized_message += escape_chars.get(bytes([byte]), bytes([byte]))
    
    return bytes(sanitized_message)






def checkServerProps(serverProps: str) -> zip:
    serverProps = "^" + serverProps
    IPv4Format = "[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}"
    hosts = re.findall(IPv4Format, serverProps)
    for host in set(hosts):
        serverProps = serverProps.replace(host, ".")
    ports = re.findall("[^0-9][0-9]{1,5}", serverProps)
    ports = [x[1:] for x in ports]
    return zip(hosts, ports)