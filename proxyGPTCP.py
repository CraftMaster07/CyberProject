import flet as ft
from threading import Thread
from proxyServer import LoadBalancer, initServers, runProxy
import logging
import time

logging.basicConfig(level=logging.DEBUG)

# Global variables to hold server and load balancer instances
communicationList = initServers()
load_balancer = LoadBalancer(communicationList)

# Available load balancing methods
LOAD_BALANCING_METHODS = ["roundRobin", "leastConnections", "random"]

def start_proxy():
    proxy_thread = Thread(target=runProxy, daemon=True)
    proxy_thread.start()
    logging.info("Proxy server started.")

def create_control_panel(page: ft.Page):
    # Function to update the load balancing method
    def update_method(e):
        method = lb_dropdown.value
        load_balancer.chooseServer(method)
        logging.info(f"Load balancing method updated to: {method}")
    
    # Function to display server statistics
    def update_statistics():
        stats = []
        for server in communicationList:
            stats.append(ft.Text(f"{server.name}: {len(server.clientList)} clients"))
        stats_column.controls = stats
        page.update()

    # Dropdown for load balancing method
    lb_dropdown = ft.Dropdown(
        label="Load Balancing Method",
        options=[ft.dropdown.Option(method) for method in LOAD_BALANCING_METHODS],
        value="roundRobin",
        on_change=update_method
    )
    
    # Button to start the proxy server
    start_button = ft.ElevatedButton(text="Start Proxy Server", on_click=lambda e: start_proxy())
    
    # Column to display server statistics
    stats_column = ft.Column()

    # Layout the controls
    page.add(
        ft.Row([lb_dropdown, start_button]),
        stats_column
    )

    # Regularly update statistics
    def refresh_statistics():
        while True:
            update_statistics()
            time.sleep(2)

    stats_thread = Thread(target=refresh_statistics, daemon=True)
    stats_thread.start()

# Run the Flet app
ft.app(target=create_control_panel)
