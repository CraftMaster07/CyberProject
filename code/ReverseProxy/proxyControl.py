import flet as ft
from connectionObjects import Server


# Color palette
color_text = "#DFF5FF"
color_new = "#5356FF"
color_secondary = "#378CE7"
color_tertiary = "#67C6E3"
color_background = "#494CEF"

SUBTITLE_TEXT_STYLE = ft.TextStyle(size=20, color=color_text, font_family="Consolas")


def main(page: ft.Page) -> None:
    page.title = "ReverseProxy Control Panel"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 950
    page.window_height = 600
    page.bgcolor = color_background

    def server_list():
        return ft.ListView(
            [
                ft.ListTile(
                    leading=ft.Icon(ft.icons.STORAGE, color=color_text),
                    subtitle=ft.Text(f"IP: {}, Port: {}, Status: {}", style=SUBTITLE_TEXT_STYLE),
                    data=server
                )
                for server in servers
            ]
        )
    
    def getDataFromDB():