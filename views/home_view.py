# views/home_view.py
import flet as ft
from typing import Callable
from core.theme_base import AppTheme

def build_home_screen(theme: AppTheme, on_navigate: Callable[[str], None]) -> ft.Container:
    def build_app_tile(title: str, icon_name: str, app_id: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon_name, size=60, color=theme.accent),
                    ft.Text(title, size=18, color=theme.text_main, weight=ft.FontWeight.W_500)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            width=160, height=160,
            bgcolor=theme.bg_panel,
            border_radius=20,
            ink=True,
            on_click=lambda e: on_navigate(app_id)
        )

    return ft.Container(
        content=ft.Row(
            controls=[
                build_app_tile("Radio", ft.Icons.RADIO, "radio"),
                build_app_tile("Bluetooth", ft.Icons.BLUETOOTH, "bluetooth"),
                build_app_tile("Telemetria", ft.Icons.SPEED, "telemetry"),
                build_app_tile("Kamera", ft.Icons.CAMERA_ALT, "manual_camera"),
                build_app_tile("Ustawienia", ft.Icons.SETTINGS, "settings"),
                build_app_tile("Aplikacje", ft.Icons.APPS, "apps"),
            ],
            wrap=True, alignment=ft.MainAxisAlignment.CENTER,
            spacing=20, run_spacing=20,
        ),
        padding=ft.Padding(left=50, top=100, right=50, bottom=0),
        expand=True
    )
