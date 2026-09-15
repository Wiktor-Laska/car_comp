# themes/mazda_night_drive/bluetooth.py
import flet as ft
from core.state import AppState
from core.theme_interface import ThemeCallbacks

def _format_duration(total_seconds: float) -> str:
    bounded_seconds = max(0, int(total_seconds))
    minutes, seconds = divmod(bounded_seconds, 60)
    return f"{minutes}:{seconds:02d}"

def render_bluetooth(theme, state: AppState, callbacks: ThemeCallbacks) -> ft.Control:
    maximum_progress = max(state.track_duration_seconds, 1.0)
    progress = min(max(state.track_elapsed_seconds, 0.0), maximum_progress)

    # 1. Placeholder na okładkę albumu (zgodnie ze specyfikacją 220x220, radius 18)
    album_art = ft.Container(
        width=220, height=220,
        bgcolor=theme.panel,
        border_radius=18,
        border=ft.Border(*[ft.BorderSide(1, theme.panel_border)]*4),
        alignment=ft.Alignment(0, 0),
        content=ft.Column([
            ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, size=64, color=theme.text_muted),
            ft.Text("BLUETOOTH\nAUDIO", size=14, color=theme.text_muted, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_600)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
    )

    # 2. Fabryka przycisków sterujących
    def transport_btn(icon: ft.IconData, size: float, bg_color: str, icon_color: str, on_click) -> ft.Container:
        return ft.Container(
            width=size, height=size,
            bgcolor=bg_color,
            border_radius=14, # Miękki radius z Twojej specyfikacji
            alignment=ft.Alignment(0, 0),
            ink=True,
            on_click=lambda _: on_click(),
            content=ft.Icon(icon, size=size * 0.5, color=icon_color)
        )

    play_icon = ft.Icons.PAUSE_ROUNDED if state.is_playing else ft.Icons.PLAY_ARROW_ROUNDED

    controls = ft.Row([
        transport_btn(ft.Icons.SKIP_PREVIOUS_ROUNDED, 64, theme.panel, theme.text_main, callbacks["prev_track"]),
        transport_btn(play_icon, 76, theme.accent, theme.text_main, callbacks["toggle_play"]),
        transport_btn(ft.Icons.SKIP_NEXT_ROUNDED, 64, theme.panel, theme.text_main, callbacks["next_track"]),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=32)

    # 3. Pasek postępu (grubszy, dostosowany do klikania palcem)
    slider = ft.Slider(
        min=0, max=maximum_progress, value=progress,
        active_color=theme.accent, inactive_color=theme.panel,
        thumb_color=theme.text_main, disabled=True,
    )

    return ft.Container(
        expand=True,
        padding=ft.Padding(50, 30, 50, 0),
        content=ft.Column([
            ft.Text("NOW PLAYING", size=14, color=theme.accent, weight=ft.FontWeight.W_600),
            ft.Container(height=20),
            ft.Row([
                album_art,
                ft.Container(width=50), # Odstęp między okładką a tekstem
                ft.Column([
                    ft.Text(state.current_track_title, size=46, weight=ft.FontWeight.BOLD, color=theme.text_main, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(state.current_track_artist, size=24, color=theme.text_muted, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Container(height=20),
                    ft.Row([
                        ft.Text(_format_duration(progress), color=theme.text_muted, size=16),
                        ft.Container(expand=True),
                        ft.Text(_format_duration(maximum_progress), color=theme.text_muted, size=16),
                    ]),
                    slider,
                    ft.Container(height=10),
                    controls
                ], expand=True, alignment=ft.MainAxisAlignment.CENTER)
            ], expand=True, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        ])
    )
