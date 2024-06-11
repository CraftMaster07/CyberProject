import flet as ft
from flet import Page, Text, Row, Column, Container, ElevatedButton, TextField, Dropdown, ListView, DataTable, DataColumn, DataRow, DataCell, Switch, RadioGroup, Radio

# Mock data for servers
servers = [
    {"ip": "192.168.1.1", "port": 8080, "status": "up", "connections": 5, "airtime": "10h", "lastConnected": "2024-05-20 10:00:00", "lastCrashed": "2024-05-18 08:00:00"},
    {"ip": "192.168.1.2", "port": 8081, "status": "down", "connections": 0, "airtime": "5h", "lastConnected": "2024-05-19 14:00:00", "lastCrashed": "2024-05-21 12:00:00"},
    {"ip": "192.168.1.3", "port": 8082, "status": "up", "connections": 10, "airtime": "15h", "lastConnected": "2024-05-22 09:30:00", "lastCrashed": "2024-05-17 07:45:00"},
    {"ip": "192.168.1.4", "port": 8083, "status": "up", "connections": 3, "airtime": "8h", "lastConnected": "2024-05-21 11:00:00", "lastCrashed": "2024-05-20 06:30:00"},
    {"ip": "192.168.1.5", "port": 8084, "status": "down", "connections": 0, "airtime": "0h", "lastConnected": "2024-05-18 15:00:00", "lastCrashed": "2024-05-22 13:15:00"},
    {"ip": "192.168.1.6", "port": 8085, "status": "up", "connections": 8, "airtime": "12h", "lastConnected": "2024-05-23 08:45:00", "lastCrashed": "2024-05-19 09:50:00"}
]

configs = ['host', 'port', 'buffer size', 'backlog', 'time format']

# Color palette
color_text = "#DFF5FF"
color_new = "#5356FF"
color_secondary = "#378CE7"
color_tertiary = "#67C6E3"
color_background = "#494CEF"#"#4346F8"

def main(page: Page):
    page.title = "ReverseProxy Control Panel"
    page.window_width = 950
    page.window_height = 600
    page.bgcolor = color_background

    # Function to display server list
    def server_list():
        return ft.ListView(
            [
                ft.ListTile(
                    leading=ft.Icon(ft.icons.STORAGE, color=color_text),
                    subtitle=ft.Text(f"IP: {server['ip']}, Port: {server['port']}, Status: {server['status']}", size=20, color=color_text),
                    data=server  # Store server data in the ListTile
                )
                for server in servers
            ],
            expand=True
        )

    # Dashboard Section
    def dashboard_view():
        return Container(
            bgcolor=color_secondary,
            expand=True,
            content=Column(
                expand=True,
                controls=[
                    Text(" Dashboard", style="headlineMedium", color=color_text),
                    Text("  Server Status:", color=color_text, size=20),
                    server_list(),
                    Text(" Load Balancing Method: Round Robin", color=color_text, size=20),
                    # Add more dashboard elements here...
                ]
            )
        )

    # Server Management Section
    server_ip = TextField(label="Server IP", border_color=color_tertiary)
    server_port = TextField(label="Server Port", border_color=color_tertiary)

    def add_server(e):
        ip = server_ip.value
        port = int(server_port.value)
        servers.append({"ip": ip, "port": port, "status": "up", "connections": 0, "airtime": "0h", "lastConnected": "N/A", "lastCrashed": "N/A"})
        server_ip.value = ""
        server_port.value = ""
        show_view(server_management_view)  # Update view to reflect changes

    def server_management_view():
        return Container(
            bgcolor=color_secondary,
            expand=True,
            content=Column(
                expand=True,
                controls=[
                    Text("Server Management", style="headlineMedium", color=color_text),
                    server_ip,
                    server_port,
                    ElevatedButton(text="Add Server", on_click=add_server, color=color_text, bgcolor=color_tertiary),
                    server_list(),
                    # Add more server management elements here...
                ]
            ),
                
        )

    # Configuration Section
    lb_method = Dropdown(
        label="Load Balancing Method",
        width=230,
        options=[
            ft.dropdown.Option(key="roundRobin", text="Round Robin"),
            ft.dropdown.Option(key="leastConnections", text="Least Connections"),
            ft.dropdown.Option(key="random", text="Random"),
            ft.dropdown.Option(key="IP Hashing", text="IP Hashing"),
        ],
        border_color=color_tertiary
    )
    retry_limit = TextField(label="Retry Limit", border_color=color_tertiary, width=230)
    
    
    choose_by_group = RadioGroup(content=Column([
        Radio(value="time", label="By Time"),
        Radio(value="user", label="By User")
    ]))

    time_interval = TextField(label="Time Interval (in seconds)", border_color=color_tertiary, value=1, width=230)

    load_servers = RadioGroup(content=Column([
        Radio(value="a", label="From Last Saved Servers"),
        Radio(value="b", label="From Default Servers")
    ]))


    def save_configuration(e):
        method = lb_method.value
        retries = int(retry_limit.value)
        chosen_by = choose_by_group.value
        print(f"Configuration saved: Method={method}, Retries={retries}, Choose Server By={chosen_by}")
        # Here you can add logic to actually save the configuration
        page.snack_bar(ft.SnackBar(Text(f"Configuration saved!", color=color_text), open=True, bgcolor=color_tertiary))

    def configuration_view():
        return Container(
            bgcolor=color_secondary,
            expand=True,
            content=Column(
                expand=True,
                controls=[
                    Text("Configuration", style="headlineMedium", color=color_text),
                    Text(height=1),
                    ElevatedButton(text="Save Configuration", on_click=save_configuration, color=color_text, bgcolor=color_tertiary),
                    Text(height=0.2),
                    lb_method,
                    retry_limit,
                    Text("Choose Server By:", color=color_text),
                    choose_by_group,
                    time_interval,
                    Text("Load Servers From:", color=color_text),
                    load_servers,
                    Row(
                        controls=[
                            Text('Host: ', color=color_text, size=20),
                            TextField(value="0.0.0.0", border_color=color_tertiary, width=230)
                        ]
                    ),
                    Row(
                        controls=[
                            Text('Port: ', color=color_text, size=20),
                            TextField(value="8080", border_color=color_tertiary, width=230)
                        ]
                    ),
                    Row(
                        controls=[
                            Text('Buffer size: ', color=color_text, size=20),
                            TextField(value="1024", border_color=color_tertiary, width=230)
                        ]
                    ),
                    Row(
                        controls=[
                            Text('Backlog: ', color=color_text, size=20),
                            TextField(value="5", border_color=color_tertiary, width=230)
                        ]
                    ),
                    Text(),
                    ElevatedButton(text="Save Configuration", on_click=save_configuration, color=color_text, bgcolor=color_tertiary),
                    Text(),
                    # Add more configuration elements here...
                ],
                scroll="auto"
            )
        )

    # Server Properties Log Section
    def server_properties_data_log_view():
        table = DataTable(
            columns=[
                DataColumn(Text("Host (IP)", color=color_text)),
                DataColumn(Text("Port", color=color_text)),
                DataColumn(Text("Connection Count", color=color_text)),
                DataColumn(Text("Air Time", color=color_text)),
                DataColumn(Text("Last Connected", color=color_text)),
                DataColumn(Text("Last Crashed", color=color_text)),
            ],
            rows=[
                DataRow(
                    cells=[
                        DataCell(Text(server["ip"], color=color_text)),
                        DataCell(Text(str(server["port"]), color=color_text)),
                        DataCell(Text(str(server["connections"]), color=color_text)),
                        DataCell(Text(server["airtime"], color=color_text)),
                        DataCell(Text(server["lastConnected"], color=color_text)),
                        DataCell(Text(server["lastCrashed"], color=color_text)),
                    ]
                )
                for server in servers
            ]
        )
        return Container(
            bgcolor=color_secondary,
            expand=True,
            content=Column(
                expand=True,
                controls=[
                    Text("Server Properties Log", style="headlineMedium", color=color_text),
                    table
                ]
            )
        )

    # Define navigation and main content containers
    navigation = Container(
        width=225,
        bgcolor=color_new,
        content=Column(
            controls=[
                Text("Navigation", style="headlineSmall", color=color_text),
                ElevatedButton(text="Dashboard", on_click=lambda e: show_view(dashboard_view), color=color_text, bgcolor=color_secondary),
                ElevatedButton(text="Server Management", on_click=lambda e: show_view(server_management_view), color=color_text, bgcolor=color_secondary),
                ElevatedButton(text="Configuration", on_click=lambda e: show_view(configuration_view), color=color_text, bgcolor=color_secondary),
                ElevatedButton(text="Server Properties Log", on_click=lambda e: show_view(server_properties_data_log_view), color=color_text, bgcolor=color_secondary),
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
            expand=True,
            controls=[
                navigation,
                main_content,
            ]
        )
    )

ft.app(target=main)
