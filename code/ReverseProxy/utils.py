import re
import bleach

def sanitizeMessage(msg: bytes) -> bytes:
    msg = msg.decode()

    msgBody = re.search("\r\n\r\n", msg)
    if msgBody:
        bodyIndex = msgBody.span()[1]
        msgHeaders = msg[:bodyIndex]
        splitHeaders = msgHeaders.split('\r\n')

        msgBody = msg[bodyIndex:]
        msgBody = bleach.clean(msgBody)
        
    newMsg = msgHeaders + msgBody
    newMsg = newMsg.encode()
    return newMsg


def checkServerProps(serverProps: str) -> zip:
    serverProps = "^" + serverProps
    IPv4Format = "[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}"
    hosts = re.findall(IPv4Format, serverProps)
    for host in set(hosts):
        serverProps = serverProps.replace(host, ".")
    ports = re.findall("[^0-9][0-9]{1,5}", serverProps)
    ports = [x[1:] for x in ports]
    return zip(hosts, ports)