import unittest
from unittest.mock import Mock, patch
from proxyServer import LoadBalancer, Server

class TestChooseServer(unittest.TestCase):
    def setUp(self):
        self.servers = [Server("127.0.0.1", 8000), Server("127.0.0.1", 8001)]
        self.lb = LoadBalancer(self.servers)

    @patch('your_module.logger')
    def test_chooseServer_roundRobin(self, mock_logger):
        server = self.lb.chooseServer("roundRobin")
        self.assertEqual(server, self.servers[0])
        self.assertEqual(self.lb.currentServerIndex, 1)
        mock_logger.debug.assert_called_with("server list: %s", self.servers)

    @patch('your_module.logger')
    def test_chooseServer_leastConnections(self, mock_logger):
        self.servers[0].clientList = [Mock()]
        server = self.lb.chooseServer("leastConnections")
        self.assertEqual(server, self.servers[1])
        mock_logger.debug.assert_called_with("server list: %s", self.servers)

    @patch('your_module.logger')
    def test_chooseServer_random(self, mock_logger):
        server = self.lb.chooseServer("random")
        self.assertIn(server, self.servers)
        mock_logger.debug.assert_called_with("server list: %s", self.servers)

    @patch('your_module.logger')
    def test_chooseServer_invalidMethod(self, mock_logger):
        server = self.lb.chooseServer("invalidMethod")
        self.assertEqual(server, self.servers[0])
        self.assertEqual(self.lb.currentServerIndex, 1)
        mock_logger.debug.assert_called_with("server list: %s", self.servers)

    @patch('your_module.logger')
    def test_chooseServer_noServers(self, mock_logger):
        self.lb.servers = []
        server = self.lb.chooseServer("roundRobin")
        self.assertIsNone(server)
        mock_logger.warning.assert_called_with("*** ALL SERVERS ARE DOWN, PLEASE CHOOSE NEW SERVERS ***")
        mock_logger.debug.assert_called_with("server list: %s", [])

    @patch('your_module.logger')
    def test_chooseServer_serverDown(self, mock_logger):
        self.lb.servers[0].runThread = False
        server = self.lb.chooseServer("roundRobin")
        self.assertEqual(server, self.servers[1])
        self.assertEqual(self.lb.servers, [self.servers[1]])
        mock_logger.debug.assert_called_with("server list: %s", self.servers)