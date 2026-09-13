# views/radio_view.py
import flet as ft
from core.theme_base import AppTheme

def build_radio_screen(theme: AppTheme) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.RADIO, size=100, color=theme.accent),
                ft.Text("RADIO FM", size=40, color=theme.text_main, weight=ft.FontWeight.BOLD),
                ft.Text("104.4 MHz", size=24, color=theme.text_muted)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        expand=True,
        alignment=ft.Alignment(0, 0)
    )
