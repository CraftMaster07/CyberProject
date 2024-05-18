import socket
import select
from threading import Thread
import re
import random
import logging
import time
from utils import checkServerProps
from server import Server, Client


HOST = '0.0.0.0'
PORT = 8080
BUFFER_SIZE = 1024
BACKLOG = 10
ERROR = "error"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(asctime)s]%(levelname)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

fileHandler = logging.FileHandler('sample.log')
fileHandler.setLevel(logging.CRITICAL)
fileHandler.setFormatter(formatter)

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(streamHandler)


class LoadBalancer:
    def __init__(self, servers: list[Server]):
        self.servers: list[Server] = servers
        self.currentServerIndex: int = 0


    def chooseServer(self, method="roundRobin") -> Server:
        if not self.servers:
            logger.error("*** ALL SERVERS ARE DOWN, PLEASE CHOOSE NEW SERVERS ***")
            self.updateServerList(initServers())
        server: Server = None

        if method == "roundRobin":
            server = self.roundRobin()
        elif method == "leastConnections":
            server = self.leastConnections()
        elif method == "random":
            server = self.random()
        else:
            server = self.roundRobin()
        
        if server.runThread:
            return server
        self.servers.remove(server)
        self.chooseServer(method)


    def updateServerList(self, serverList: list[Server]):
        self.servers = serverList
        self.currentServerIndex = 0
    

    def roundRobin(self) -> Server:
        server = self.servers[self.currentServerIndex]
        self.currentServerIndex = (self.currentServerIndex + 1) % len(self.servers)
        return server

    def leastConnections(self) -> Server: 
        return min(self.servers, key=lambda server: len(server.clientList))
    

    def random(self) -> Server:
        return self.servers[random.randint(0, len(self.servers) - 1)]



def initProxy() -> socket.socket:
    proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxySocket.bind((HOST, PORT))
    logger.info("Proxy is up and running!")

    return proxySocket


def initServers(communicationList: list[Server] = []) -> list[Server]:
    continueAsking = True
    while continueAsking:
        logger.info("Enter 1 or more servers' IPs and ports (i.e. 127.0.0.1, 12345): ")
        serverProps = input()
        serverProps = checkServerProps(serverProps)
        communicationList.extend(Server(host, int(port)) for host, port in serverProps)
        logger.info("Add more servers? (Y/N)")
        serverProps = input()
        continueAsking = bool(re.search("[Y,y]", serverProps))
    if communicationList:
        logger.info("Server(s): " + ", ".join([str(x.name) for x in communicationList]))
        for server in communicationList:
            server.startThread()
    else:
        logger.info("No Servers were Chosen")
        serverProps = initServers(communicationList)
    return communicationList


def lookForClients(communicationList: list[Server], proxySocket: socket.socket):
    proxyLoadBalancer = LoadBalancer(communicationList)
    while True:
        if not communicationList:
            communicationList = initServers()
        currentServer = proxyLoadBalancer.chooseServer("leastConnections")
        if currentServer is None:
            logger.error("No servers are available to handle client requests.")
            time.sleep(5)  # Wait before retrying to avoid busy-waiting
            continue

        readList, _, _ = select.select([proxySocket], [], []) # need to get server status
        for sock in readList:
            if sock is proxySocket:
                getNewClient(proxySocket, currentServer)


def getNewClient(proxySocket: socket.socket, chosenServer: Server):
    clientSocket, clientAddress = proxySocket.accept()
    newClient = Client(*clientAddress, clientSocket)
    logger.debug(f"New Client Joined: {newClient.name}")

    if chosenServer is None:
        logger.error("No valid server available to handle the new client.")
        newClient.closeConnection()
        return

    chosenServer.insertClient(newClient)


def runProxy():
    communicationList = initServers()
    proxySocket = initProxy()

    proxySocket.listen(BACKLOG)
    logger.info(f"Server listening on port {PORT}...")
    lookForClients(communicationList, proxySocket,)


def main():
    runProxy()


if __name__ == "__main__":
    main()
