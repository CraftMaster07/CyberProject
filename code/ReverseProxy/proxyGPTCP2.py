import flet as ft
from flet import Page, Text, Row, Column, Container, ElevatedButton, TextField, Dropdown, ListView

# Mock data for servers
servers = [{"ip": "192.168.1.1", "port": 8080, "status": "up", "connections": 5}]

def main(page: Page):
    page.title = "Load Balancer Control Panel"
    page.window_width = 800
    page.window_height = 600

    # Function to display server list
    def server_list():
        return ListView(
            [
                Text(f"IP: {server['ip']}, Port: {server['port']}, Status: {server['status']}, Connections: {server['connections']}")
                for server in servers
            ],
            expand=True
        )

    # Dashboard Section
    def dashboard_view():
        return Column(
            [
                Text("Dashboard", style="headlineMedium"),
                Text("Server Status:"),
                server_list(),
                Text("Load Balancing Method: Round Robin"),
                # Add more dashboard elements here...
            ],
            expand=True
        )

    # Server Management Section
    server_ip = TextField(label="Server IP")
    server_port = TextField(label="Server Port")

    def add_server(e):
        ip = server_ip.value
        port = int(server_port.value)
        servers.append({"ip": ip, "port": port, "status": "up", "connections": 0})
        server_ip.value = ""
        server_port.value = ""
        page.update()

    def server_management_view():
        return Column(
            [
                Text("Server Management", style="headlineMedium"),
                server_ip,
                server_port,
                ElevatedButton(text="Add Server", on_click=add_server),
                server_list(),
                # Add more server management elements here...
            ],
            expand=True
        )

    # Configuration Section
    lb_method = Dropdown(
        label="Load Balancing Method",
        options=[
            ft.dropdown.Option(key="roundRobin", text="Round Robin"),
            ft.dropdown.Option(key="leastConnections", text="Least Connections"),
            ft.dropdown.Option(key="random", text="Random"),
        ],
    )
    retry_limit = TextField(label="Retry Limit")

    def save_configuration(e):
        # Save configuration logic
        method = lb_method.value
        retries = int(retry_limit.value)
        print(f"Configuration saved: Method={method}, Retries={retries}")
        page.update()

    def configuration_view():
        return Column(
            [
                Text("Configuration", style="headlineMedium"),
                lb_method,
                retry_limit,
                ElevatedButton(text="Save Configuration", on_click=save_configuration),
                # Add more configuration elements here...
            ],
            expand=True
        )

    # Define navigation and main content containers
    navigation = Container(
        width=200,
        content=Column(
            [
                Text("Navigation", style="headlineSmall"),
                ElevatedButton(text="Dashboard", on_click=lambda e: show_view(dashboard_view)),
                ElevatedButton(text="Server Management", on_click=lambda e: show_view(server_management_view)),
                ElevatedButton(text="Configuration", on_click=lambda e: show_view(configuration_view)),
            ],
            spacing=10,
        ),
    )

    main_content = Container(expand=True)

    # Function to switch views
    def show_view(view_fn):
        main_content.content = view_fn()
        page.update()

    # Initialize with the dashboard view
    show_view(dashboard_view)

    # Main Layout
    page.add(
        Row(
            [
                navigation,
                main_content,
            ],
            expand=True
        )
    )

ft.app(target=main)
