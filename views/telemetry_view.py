# views/telemetry_view.py
import flet as ft
from core.theme_base import AppTheme

def build_telemetry_screen(theme: AppTheme) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.SPEED, size=100, color=theme.accent),
                ft.Text("TELEMETRIA OBD2 / CAN", size=30, color=theme.text_main),
                ft.Text("Czekam na dane z ECU...", size=18, color=theme.text_muted)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        expand=True,
        alignment=ft.Alignment(0, 0)
    )
