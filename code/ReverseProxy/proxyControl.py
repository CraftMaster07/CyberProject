# TODO:
# add configureation
# read from file


import flet as ft
from connectionObjects import Server
import proxyServer
from threading import Thread

# Color palette
color_text = "#DFF5FF"
color_new = "#5356FF"
color_secondary = "#378CE7"
color_tertiary = "#67C6E3"
color_background = "#494CEF"

SUBTITLE_TEXT_STYLE = ft.TextStyle(size=20, color=color_text)
SMALL_TEXT_STYLE = ft.TextStyle(size=14, color=color_text, font_family="Poppins")

loadFrom = "database"

def main(page: ft.Page) -> None:
    servers = proxyServer.initServers(proxyServer.addSavedServers() if loadFrom == "database" else None)
    proxyThread = Thread(target=proxyServer.runProxy, args=(servers,))
    proxyThread.start()

    page.title = "ReverseProxy Control Panel"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 950
    page.window_height = 600
    page.bgcolor = color_background

    mainContent = ft.Container(expand=True)
    serverIp = ft.TextField(label="Server IP", border_color=color_tertiary, width=230, max_length=proxyServer.MAX_HOST_LENGTH)
    serverPort = ft.TextField(label="Server Port", border_color=color_tertiary, width=230, max_length=proxyServer.MAX_PORT_LENGTH)

    loadBalancingMethod = ft.Dropdown(
        label="Load Balancing Method",
        options=[
            ft.dropdown.Option(key="roundRobin", text="Round Robin"),
            ft.dropdown.Option(key="leastConnections", text="Least Connections"),
            ft.dropdown.Option(key="random", text="Random"),
            ft.dropdown.Option(key="IP Hashing", text="IP Hashing"),
        ],
        border_color=color_tertiary,
        width=230
    )

    chooseServerBy = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="time", label = "By Time", label_style=SUBTITLE_TEXT_STYLE),
        ft.Radio(value="client", label = "By Client", label_style=SUBTITLE_TEXT_STYLE)
    ]))

    timeInterval = ft.TextField(label="Time Interval (in seconds)", border_color=color_tertiary, width=230)

    loadServersFrom = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="database", label = "Last Saved Servers", label_style=SUBTITLE_TEXT_STYLE),
        ft.Radio(value="file", label = "Default Servers (in config.json)", label_style=SUBTITLE_TEXT_STYLE)
    ]))

    navigation = ft.Container(
        width=255,
        bgcolor=color_new,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("Navigation", style="headlineMedium", color=color_text),
                ft.ElevatedButton(text="Dashboard", color=color_text, bgcolor=color_secondary, on_click=lambda e:showView(dashboardView)),
                ft.ElevatedButton(text="Server Management", color=color_text, bgcolor=color_secondary, on_click=lambda e:showView(serverManagementView)),
                ft.ElevatedButton(text="Configuration", color=color_text, bgcolor=color_secondary, on_click=lambda e:showView(configurationView)),
                ft.ElevatedButton(text="Server Properties Log", color=color_text, bgcolor=color_secondary, on_click=lambda e:showView(serverPropertiesDataLogView)),
            ],
            spacing=10
        )
    )

    def serverList():
        return ft.ListView(
            [
                ft.ListTile(
                    leading=ft.Icon(ft.icons.STORAGE, color=color_text),
                    subtitle=ft.Text(f"IP: {server.host}, Port: {server.port}, Status: UP", style=SUBTITLE_TEXT_STYLE),
                    data=server
                )
                for server in servers
            ],
            expand=True
        )
    
    def dashboardView():
        return ft.Container(
            bgcolor=color_secondary,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(" Dashboard", style="headlineMedium", color=color_text),
                    ft.Text("  Server Status:", style=SUBTITLE_TEXT_STYLE),
                    serverList(),
                    ft.Text(" Load Balancing Method: Round Robin", style=SUBTITLE_TEXT_STYLE),
                    # Add more dashboard elements here...
                ]
            )
        )
    

    def addServer(e):
        nonlocal servers
        serverProps = serverPort.value + " " + serverIp.value
        if list(proxyServer.checkServerProps(serverProps)):
            servers = proxyServer.addServers(serverProps, servers)
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Server added!", style=SUBTITLE_TEXT_STYLE), open=True, bgcolor=color_tertiary)
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"invalid server arguments", style=SUBTITLE_TEXT_STYLE), open=True, bgcolor=color_tertiary)
        serverIp.value = ""
        serverPort.value = ""
        showView(serverManagementView)
    

    def serverManagementView():
        return ft.Container(
            bgcolor=color_secondary,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(" Server Management", style="headlineMedium", color=color_text),
                    ft.Row(
                        [
                            serverIp,
                            serverPort
                        ],
                        spacing=10
                    ),
                    ft.ElevatedButton("Add Server", on_click=addServer, color=color_text, bgcolor=color_tertiary),
                    serverList()
                    # Add more server management elements here...
                ]
            )
        )


    def saveConfig(e):
        method = loadBalancingMethod.value
        chosenBy = chooseServerBy.value
        loadFrom = loadServersFrom.value
        coosheTime = timeInterval.value
        page.snack_bar = ft.SnackBar(ft.Text(f"Configuration saved!", style=SUBTITLE_TEXT_STYLE), open=True, bgcolor=color_tertiary)


    def configurationView():
        return ft.Container(
            bgcolor=color_secondary,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(" Configuration", style="headlineMedium", color=color_text),
                    ft.Text(height=1),
                    ft.ElevatedButton("Save Configuration", on_click=saveConfig, color=color_text, bgcolor=color_tertiary),
                    ft.Text(height=0.2),
                    loadBalancingMethod,
                    ft.Text("Choose Server By:", style=SUBTITLE_TEXT_STYLE),
                    chooseServerBy,
                    timeInterval,
                    ft.Text("Load Servers From:", style=SUBTITLE_TEXT_STYLE),
                    loadServersFrom,
                    ft.Row(
                        controls=[
                            ft.Text('Host: ', style=SUBTITLE_TEXT_STYLE, width=100),
                            ft.TextField(value=proxyServer.HOST, text_style=SUBTITLE_TEXT_STYLE, width=230)
                        ],
                    ),
                    ft.Row(
                        controls=[
                            ft.Text('Port: ', style=SUBTITLE_TEXT_STYLE, width=100),
                            ft.TextField(value=proxyServer.PORT, text_style=SUBTITLE_TEXT_STYLE, width=230)
                        ],
                    ),

                    ft.Row(
                        controls=[
                            ft.Text('Buffer size: ', style=SUBTITLE_TEXT_STYLE, width=100),
                            ft.TextField(value=proxyServer.BUFFER_SIZE, text_style=SUBTITLE_TEXT_STYLE, width=230)
                        ],
                    ),

                    ft.Row(
                        controls=[
                            ft.Text('Backlog: ', style=SUBTITLE_TEXT_STYLE, width=100),
                            ft.TextField(value=proxyServer.BACKLOG, text_style=SUBTITLE_TEXT_STYLE, width=230)
                        ],
                    ),

                    ft.ElevatedButton("Save Configuration", on_click=saveConfig, color=color_text, bgcolor=color_tertiary),
                    # Add more configuration elements here...
                ],
                scroll="auto"
            )
        )
    
    def serverPropertiesDataLogView():
        airTimeList = proxyServer.getTimes(servers)
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Host (IP)", style=SMALL_TEXT_STYLE)),
                ft.DataColumn(ft.Text("Port", style=SMALL_TEXT_STYLE)),
                ft.DataColumn(ft.Text("Connections", style=SMALL_TEXT_STYLE)),
                ft.DataColumn(ft.Text("Air Time", style=SMALL_TEXT_STYLE)),
                ft.DataColumn(ft.Text("Last Connected", style=SMALL_TEXT_STYLE)),
                ft.DataColumn(ft.Text("Last Crashed", style=SMALL_TEXT_STYLE)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(server.host, style=SMALL_TEXT_STYLE)),
                        ft.DataCell(ft.Text(server.port, style=SMALL_TEXT_STYLE)),
                        ft.DataCell(ft.Text(server.clientCount, style=SMALL_TEXT_STYLE)),
                        ft.DataCell(ft.Text(next(airTimeList) + int(proxyServer.time.time() - server.lastCheckedTime), style=SMALL_TEXT_STYLE)),
                        ft.DataCell(ft.Text(server.lastRequestTime, style=SMALL_TEXT_STYLE)),
                        ft.DataCell(ft.Text(server.lastCrashTime, style=SMALL_TEXT_STYLE)),
                    ]
                )
                for server in servers
            ],
            expand=True
        )
        return ft.Container(
            bgcolor=color_secondary,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(" Server Properties Log", style="headlineMedium", color=color_text),
                    table
                ]
            )
        )

    def showView(viewFn):
        mainContent.content = viewFn()
        page.update()

    def checkServersAlive():
        nonlocal servers
        while True:
            if not servers:
                print("no servers found")
                page.snack_bar = ft.SnackBar(ft.Text(f"*** ALL SERVERS ARE DOWN, PLEASE CHOOSE NEW SERVERS ***", style=SUBTITLE_TEXT_STYLE), open=True, bgcolor=color_tertiary)
            proxyServer.time.sleep(10)
    
    showView(dashboardView)

    page.add(
        ft.Row(
            expand=True,
            controls=[
                navigation,
                mainContent
            ]
        )
    )

    serversAliveThread = Thread(target=checkServersAlive)
    serversAliveThread.start()

if __name__ == "__main__":
    ft.app(target=main)