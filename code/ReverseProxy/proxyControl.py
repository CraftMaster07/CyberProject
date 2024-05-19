import flet as ft
from flet import TextField
from flet_core.control_event import ControlEvent


def main(page: ft.Page) -> None:
    page.title = "Proxy Control"
    page.theme_mode = ft.ThemeMode.DARK