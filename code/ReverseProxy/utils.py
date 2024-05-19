# utils.py

import re
import bleach
import html

def sanitizeMessage(msg: bytes) -> bytes:
    msg = msg.decode('utf-8', errors='ignore')

    headerEnd = msg.find("\r\n\r\n")
    if headerEnd == -1:
        return msg

    header = msg[:headerEnd]
    body = msg[headerEnd + 4:]

    sanitizedBody = bleach.clean(body, tags=bleach.sanitizer.ALLOWED_TAGS, attributes=bleach.sanitizer.ALLOWED_ATTRIBUTES)

    sanitizedMsg = header.encode('utf-8') + b"\r\n\r\n" + sanitizedBody.encode('utf-8')
    return sanitizedMsg


def checkServerProps(serverProps: str) -> zip:
    serverProps = "^" + serverProps
    IPv4Format = "[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}"
    hosts = re.findall(IPv4Format, serverProps)
    for host in set(hosts):
        serverProps = serverProps.replace(host, ".")
    ports = re.findall("[^0-9][0-9]{1,5}", serverProps)
    ports = [x[1:] for x in ports]
    return zip(hosts, ports)