"""Settings controls for the Dark Modern theme."""

import flet as ft

from core.state import ThemeId
from core.theme_interface import ThemeChangeCallback


def build_settings_screen(
    *,
    active_theme_id: ThemeId,
    on_theme_change: ThemeChangeCallback,
    background_color: str,
    panel_color: str,
    accent_color: str,
    text_color: str,
    muted_text_color: str,
) -> ft.Control:
    """Build a theme selector without coupling it to controller state."""
    target_theme: ThemeId = (
        "mazda_classic" if active_theme_id == "dark_modern" else "dark_modern"
    )
    target_label = (
        "Mazda Classic" if target_theme == "mazda_classic" else "Dark Modern"
    )

    return ft.Container(
        expand=True,
        bgcolor=background_color,
        alignment=ft.Alignment(0, 0),
        content=ft.Container(
            width=560,
            padding=32,
            bgcolor=panel_color,
            border_radius=20,
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.PALETTE_OUTLINED, size=64, color=accent_color),
                    ft.Text(
                        "USTAWIENIA WYGLĄDU",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        color=text_color,
                    ),
                    ft.Text(
                        f"Aktywny motyw: {active_theme_id.replace('_', ' ').title()}",
                        color=muted_text_color,
                    ),
                    ft.Container(height=16),
                    ft.ElevatedButton(
                        content=ft.Text(
                            f"Przełącz na {target_label}",
                            color=text_color,
                            weight=ft.FontWeight.BOLD,
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=accent_color,
                            padding=ft.Padding(left=24, top=18, right=24, bottom=18),
                            shape=ft.RoundedRectangleBorder(radius=12),
                        ),
                        on_click=lambda _: on_theme_change(target_theme),
                    ),
                ],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
        ),
    )
