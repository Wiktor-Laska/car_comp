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

    # 1. Wizualizacja: Okładka (Album Art) LUB Tekst Piosenki (Lyrics)
    if state.is_lyrics_visible:
        # Widok tekstu (skrolowany)
        media_display = ft.Container(
            width=260, height=260,
            bgcolor=theme.panel,
            border_radius=18,
            border=ft.Border(*[ft.BorderSide(1, theme.accent)]*4), # Czerwona ramka sygnalizuje tryb tekstu
            padding=16,
            content=ft.ListView(
                controls=[ft.Text(state.lyrics_text, color=theme.text_main, size=16, text_align="center")],
                expand=True, spacing=10
            )
        )
    else:
            # Widok okładki albumu
        if state.album_art_url:
            # Zmieniamy fit=ft.ImageFit.COVER na fit="cover"
            media_display = ft.Image(src=state.album_art_url, width=260, height=260, fit="cover", border_radius=18)

        else:
            media_display = ft.Container(
                width=260, height=260, bgcolor=theme.panel, border_radius=18,
                border=ft.Border(*[ft.BorderSide(1, theme.panel_border)]*4),
                content=ft.Column([
                    ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, size=64, color=theme.text_muted),
                    ft.Text("BLUETOOTH\nAUDIO", size=14, color=theme.text_muted, text_align="center")
                ], alignment="center", horizontal_alignment="center", spacing=8)
            )

    # 2. Fabryka przycisków
    def transport_btn(icon, size, bg_color, icon_color, on_click):
        return ft.Container(
            width=size, height=size, bgcolor=bg_color, border_radius=14,
            alignment=ft.Alignment(0, 0), ink=True, on_click=lambda _: on_click(),
            content=ft.Icon(icon, size=size * 0.5, color=icon_color)
        )

    play_icon = ft.Icons.PAUSE_ROUNDED if state.is_playing else ft.Icons.PLAY_ARROW_ROUNDED

    controls = ft.Row([
        transport_btn(ft.Icons.SKIP_PREVIOUS_ROUNDED, 64, theme.panel, theme.text_main, callbacks["prev_track"]),
        transport_btn(play_icon, 76, theme.accent, theme.text_main, callbacks["toggle_play"]),
        transport_btn(ft.Icons.SKIP_NEXT_ROUNDED, 64, theme.panel, theme.text_main, callbacks["next_track"]),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=32)

    slider = ft.Slider(
        min=0, max=maximum_progress, value=progress,
        active_color=theme.accent, inactive_color=theme.panel,
        thumb_color=theme.text_main, disabled=True,
    )

    return ft.Container(
        expand=True, padding=ft.Padding(50, 20, 50, 0),
        content=ft.Column([
            # Górny pasek BT
            ft.Row([
                ft.Text("NOW PLAYING", size=14, color=theme.accent, weight=ft.FontWeight.W_600),
                ft.Container(expand=True),
                # Przycisk włączania tekstu piosenki (Lyrics)
                # Przycisk włączania tekstu piosenki (Lyrics)
                ft.OutlinedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LYRICS_ROUNDED if state.is_lyrics_visible else ft.Icons.LYRICS_OUTLINED),
                        ft.Text("LYRICS", weight=ft.FontWeight.BOLD)
                    ], tight=True, spacing=8),
                    style=ft.ButtonStyle(
                        color=theme.accent if state.is_lyrics_visible else theme.text_muted,
                        side=ft.BorderSide(1, theme.accent if state.is_lyrics_visible else theme.panel_border),
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding(16, 8, 16, 8),
                    ),
                    on_click=lambda _: callbacks["toggle_lyrics"]()
                )
            ]),
            ft.Container(height=10),

            # Główny interfejs (Kładka po lewej, dane po prawej)
            ft.Row([
                media_display,
                ft.Container(width=50),
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
