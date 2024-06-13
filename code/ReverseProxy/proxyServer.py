# proxyServer.py

import socket
import select
from threading import Thread
import re
import random
import logging
import time
from utils import checkServerProps
from connectionObjects import Server, Client
import hashlib
import sqlite3

# user configuration
method = "roundRobin"
chosenBy = "time"
loadFrom = "database"
coosheTime = 1
useIPHashing = True
chosenBy = True  # every set amount of time or choose server for each client


HOST = '0.0.0.0'
MAX_HOST_LENGTH = 15
PORT = 8080
MAX_PORT_LENGTH = 5
BUFFER_SIZE = 1024
BACKLOG = 10
ERROR = "error"
TIME_INTERVAL = 1
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


con = sqlite3.connect("serverData.db", check_same_thread=False)
cur = con.cursor()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s]%(levelname)s: %(message)s",
                              TIME_FORMAT)
fileHandler = logging.FileHandler('sample.log')
fileHandler.setLevel(logging.CRITICAL)
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)


class LoadBalancer:
    def __init__(self, servers: list[Server], allowInput: bool = False):
        self.servers: list[Server] = servers
        self.currentServerIndex: int = 0
        self.allowInput: bool = allowInput


    def chooseServer(self, method="roundRobin") -> Server:
        if not self.servers:
            logger.error("*** ALL SERVERS ARE DOWN, PLEASE CHOOSE NEW SERVERS ***")
            if not self.allowInput:
                return None
            self.updateServerList(initServersInput())
        server: Server = None

        if method == "roundRobin":
            server = self.roundRobin()
        elif method == "leastConnections":
            server = self.leastConnections()
        elif method == "random":
            server = self.random()
        else:
            logger.error(f"Invalid method: {method}, defaulting to 'roundRobin'")
            server = self.roundRobin()
        
        updateDB(self.servers)
        if server.runThread:
            return server
        self.servers.remove(server)
        self.chooseServer(method)


    def updateServerList(self, serverList: list[Server]):
        self.servers = serverList
        self.currentServerIndex = 0
    

    def getServerForClient(self, client: Client) -> Server:
        if not self.servers:
            logger.error("*** ALL SERVERS ARE DOWN, PLEASE CHOOSE NEW SERVERS ***")
            self.updateServerList(initServersInput())

        server: Server = None
        index = getServerIndex(client.host, len(self.servers))
        server = self.servers[index]
        
        if server.runThread:
            return server
        self.servers.remove(server)
        self.currentServerIndex = 0
        self.getServerForClient(client)

    def roundRobin(self) -> Server:
        try:
            server = self.servers[self.currentServerIndex]
        except IndexError:
            self.currentServerIndex = 0
            server = self.servers[self.currentServerIndex]
        self.currentServerIndex = (self.currentServerIndex + 1) % len(self.servers)
        return server

    def leastConnections(self) -> Server: 
        return min(self.servers, key=lambda server: len(server.clientList))
    

    def random(self) -> Server:
        return self.servers[random.randint(0, len(self.servers) - 1)]

proxyLoadBalancer = LoadBalancer([], True if __name__ == "__main__" else False)

def initProxy() -> socket.socket:
    proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxySocket.bind((HOST, PORT))
    logger.info("Proxy is up and running!")

    return proxySocket


def initServersInput(communicationList: list[Server] = []) -> list[Server]:
    continueAsking = True
    serverProps = ""
    while continueAsking:
        logger.info("Enter 1 or more servers' IPs and ports (i.e. 127.0.0.1, 12345): ")
        serverProps += input()
        logger.info("Add more servers? (Y/N)")
        continueAsking = bool(re.search("[Y,y]", input()))
    communicationList = addServers(serverProps, communicationList)
    if not communicationList:
        logger.info("No Servers were Chosen")
        initServersInput(communicationList)
    return communicationList

        


def addServers(serverProps: str, communicationList: list[Server] = []) -> list[Server]:
    updateDB(communicationList)
    serverProps = checkServerProps(serverProps)
    communicationList.extend(Server(host, int(port)) for host, port in serverProps)
    seen = set()
    communicationList = [x for x in communicationList if not (x.host, x.port) in seen and not seen.add((x.host, x.port))]
    updateDataFromDB(communicationList)
    return initServers(communicationList)


def initServers(communicationList: list[Server] = []) -> list[Server]:
    if communicationList:
        logger.info("Server(s): " + ", ".join([str(x.name) for x in communicationList]))

        data = [(x.host, x.port) for x in communicationList]
        cur.executemany(
            """
            INSERT OR IGNORE INTO serverData (host, port) VALUES (?, ?)
        """, data
        )
        con.commit()
        for server in communicationList:
            server.startThread()
    return communicationList


def lookForClients(communicationList: list[Server], proxySocket: socket.socket, allowInput: bool = False):
    proxyLoadBalancer.updateServerList(communicationList)
    timeLoopThread = Thread(target=chosenByLoop, args=(proxyLoadBalancer,))
    timeLoopThread.start()

    while True:
        if not communicationList:
            logger.error("*** ALL SERVERS ARE DOWN, PLEASE CHOOSE NEW SERVERS ***")
            if allowInput:
                communicationList = initServersInput(communicationList)
            else:
                time.sleep(3)

        readList, _, _ = select.select([proxySocket], [], []) # need to get server status
        for sock in readList:
            if sock is proxySocket:
                getNewClient(proxySocket, proxyLoadBalancer)


def getServerIndex(clientIP, serversLength):
    hashValue = int(hashlib.md5(clientIP.encode()).hexdigest(), 16)
    return hashValue % serversLength

def getNewClient(proxySocket: socket.socket, proxyLoadBalancer: LoadBalancer):
    global chosenServer

    clientSocket, clientAddress = proxySocket.accept()
    newClient = Client(*clientAddress, clientSocket)
    logger.debug(f"New Client Joined: {newClient.name}")
    if chosenBy:
        pass
    elif method == "IPHashing":
        chosenServer = proxyLoadBalancer.getServerForClient(newClient)
    else:
        chosenServer = proxyLoadBalancer.chooseServer("roundRobin")

    if chosenServer is None:
        logger.error("No valid server available to handle the new client.")
        newClient.closeConnection()
        return

    chosenServer.insertClient(newClient)


def getServersFromDB() -> list[Server]:
    try:
        cur.execute("SELECT host, port FROM serverData ORDER BY host, port")
        return addServers(str(cur.fetchall()))
    except sqlite3.OperationalError:
        logger.info("No server data in DB")
        return []


def addSavedServersInput():
    logger.info("Add last saved servers? (Y/N)")
    if re.search("[Y,y]", input()):
        return getServersFromDB()
    return []


def addSavedServers(flag: bool = True):
    if flag:
        return getServersFromDB()


def getTimes(servers: list[Server]) -> list[int]:
    '''
    returns an iterator of air times
    '''
    airTimeList = []
    for host, port in [(server.host, server.port) for server in servers]:
        cur.execute(
            """
            SELECT airTime FROM serverData
            WHERE host = ? AND port = ?
            """,
            (host, port) 
        )
        try:
            airTime = cur.fetchone()[0]
        except TypeError:
            airTime = None
        if not airTime:
            airTimeList.append(0)
            continue
        airTimeList.append(int(float(airTime)))

    return iter(airTimeList)

def updateDB(servers: list[Server]):
    if not servers:
        return
    
    airTimeList = getTimes(servers)
    cur.executemany(
        """
        UPDATE serverData
        SET connectionsCount = ?, airTime = ?, lastConnected = ?, lastCrashed = ?
        WHERE host = ? AND port = ?
        """,
        [(server.clientCount, next(airTimeList) + int(time.time() - server.lastCheckedTime), server.lastRequestTime, server.lastCrashTime, server.host, server.port) for server in servers]
    )
    con.commit()
    for server in servers:
        server.lastCheckedTime = int(time.time())


def updateDataFromDB(servers: list[Server]):
    if not servers:
        return
    for server in servers:
        cur.execute(
            """
            SELECT connectionsCount, lastConnected, lastCrashed FROM serverData
            WHERE host = ? AND port = ?
            """,
            (server.host, server.port)
        )
        serverProps = cur.fetchone()
        if serverProps:
            server.clientCount, server.lastRequestTime, server.lastCrashTime = serverProps



def chosenByLoop(proxyLoadBalancer: LoadBalancer):
    global chosenServer
    
    while chosenBy:
        chosenServer = proxyLoadBalancer.chooseServer()
        time.sleep(TIME_INTERVAL)


def initDB():
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS serverData (
            host TEXT,
            port INTEGER,
            connectionsCount INTEGER DEFAULT 0,
            airTime TEXT DEFAULT 0,
            lastConnected TEXT DEFAULT 'N/A',
            lastCrashed TEXT DEFAULT 'N/A',
            UNIQUE(host, port)
        )
        """
    )
    con.commit()


def runProxy(servers: list[Server] = [], allowInput: bool = False):
    initDB()
    if allowInput:
        servers = initServersInput(addSavedServersInput())
    proxySocket = initProxy()

    proxySocket.listen(BACKLOG)
    logger.info(f"Server listening on port {PORT}...")
    lookForClients(servers, proxySocket, allowInput)


def main():
    runProxy([], True)


if __name__ == "__main__":
    main()
