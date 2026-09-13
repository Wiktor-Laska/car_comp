"""Bluetooth media-player screen for the Dark Modern theme."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import flet as ft

from core.state import AppState
from core.theme_interface import ThemeCallbacks

if TYPE_CHECKING:
    from themes.dark_modern.theme import DarkModernTheme


def _format_duration(total_seconds: float) -> str:
    """Format a non-negative media duration as minutes and seconds."""
    bounded_seconds = max(0, int(total_seconds))
    minutes, seconds = divmod(bounded_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def build_bluetooth_screen(
    *,
    theme: DarkModernTheme,
    state: AppState,
    callbacks: ThemeCallbacks,
) -> ft.Control:
    """Build a touch-friendly Bluetooth player using only local Flet controls."""
    maximum_progress = max(state.track_duration_seconds, 1.0)
    progress = min(max(state.track_elapsed_seconds, 0.0), maximum_progress)
    connection_icon = (
        ft.Icons.BLUETOOTH_CONNECTED
        if state.bt_connected
        else ft.Icons.BLUETOOTH_DISABLED
    )
    connection_label = state.bt_status_message or "Brak połączenia Bluetooth"
    connection_color = theme.accent if state.bt_connected else theme.text_muted
    connection_action = "ROZŁĄCZ" if state.bt_connected else "POŁĄCZ"
    play_icon = ft.Icons.PAUSE_ROUNDED if state.is_playing else ft.Icons.PLAY_ARROW_ROUNDED
    play_label = "Wstrzymaj" if state.is_playing else "Odtwórz"
    controls_disabled = not state.bt_connected

    def transport_button(
        icon: ft.IconData,
        tooltip: str,
        on_click: Callable[[], None],
        *,
        is_primary: bool = False,
    ) -> ft.Container:
        button_size = 76 if is_primary else 62
        return ft.Container(
            width=button_size,
            height=button_size,
            border_radius=button_size / 2,
            bgcolor=theme.accent if is_primary else theme.panel,
            border=(
                None
                if is_primary
                else ft.Border(*[ft.BorderSide(1, theme.accent)] * 4)
            ),
            alignment=ft.Alignment(0, 0),
            content=ft.IconButton(
                icon=icon,
                icon_size=42 if is_primary else 34,
                icon_color=theme.bg if is_primary else theme.accent,
                tooltip=tooltip,
                disabled=controls_disabled,
                on_click=lambda _: on_click(),
            ),
        )

    return ft.Container(
        expand=True,
        padding=ft.Padding(left=56, top=24, right=56, bottom=20),
        content=ft.Column(
            controls=[
                ft.Container(
                    height=54,
                    padding=ft.Padding(left=16, top=0, right=16, bottom=0),
                    bgcolor=theme.panel,
                    border_radius=12,
                    content=ft.Row(
                        controls=[
                            ft.Icon(connection_icon, color=theme.accent, size=28),
                            ft.Text(
                                "BLUETOOTH AUDIO",
                                color=theme.text_main,
                                size=17,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(expand=True),
                            ft.Text(connection_label, color=connection_color, size=14),
                            ft.OutlinedButton(
                                content=ft.Text(
                                    connection_action,
                                    color=theme.accent,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                style=ft.ButtonStyle(
                                    side=ft.BorderSide(1, theme.accent),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=lambda _: (
                                    callbacks["disconnect_bluetooth"]()
                                    if state.bt_connected
                                    else callbacks["connect_bluetooth"]()
                                ),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
                ft.Container(expand=True),
                ft.Container(
                    width=190,
                    height=190,
                    border_radius=26,
                    bgcolor=theme.panel,
                    border=ft.Border(*[ft.BorderSide(2, theme.accent)] * 4),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.ALBUM_ROUNDED,
                        color=theme.accent,
                        size=102,
                    ),
                ),
                ft.Text(
                    state.current_track_title,
                    color=theme.text_main,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(
                    state.current_track_artist,
                    color=theme.text_muted,
                    size=17,
                    text_align=ft.TextAlign.CENTER,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Container(height=4),
                ft.Slider(
                    min=0,
                    max=maximum_progress,
                    value=progress,
                    active_color=theme.accent,
                    inactive_color=theme.panel,
                    thumb_color=theme.accent,
                    disabled=True,
                ),
                ft.Row(
                    controls=[
                        ft.Text(_format_duration(progress), color=theme.text_muted),
                        ft.Container(expand=True),
                        ft.Text(
                            _format_duration(maximum_progress),
                            color=theme.text_muted,
                        ),
                    ],
                ),
                ft.Row(
                    controls=[
                        transport_button(
                            ft.Icons.SKIP_PREVIOUS_ROUNDED,
                            "Poprzedni utwór",
                            callbacks["prev_track"],
                        ),
                        transport_button(
                            play_icon,
                            play_label,
                            callbacks["toggle_play"],
                            is_primary=True,
                        ),
                        transport_button(
                            ft.Icons.SKIP_NEXT_ROUNDED,
                            "Następny utwór",
                            callbacks["next_track"],
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=28,
                ),
                ft.Container(expand=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
    )
