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

    # 1. Wizualizacja: Okładka (Album Art) LUB Tekst Piosenki (Lyrics Karaoke)
    if state.is_lyrics_visible:
        lyrics_controls = []

        # Jeśli mamy zsynchronizowany tekst (Karaoke Mode)
        if state.parsed_lyrics:
            active_idx = 0
            # Szukamy, która linijka jest aktualna na podstawie sekund
            for i, (time_sec, text) in enumerate(state.parsed_lyrics):
                if time_sec <= state.track_elapsed_seconds:
                    active_idx = i
                else:
                    break

            # Wyświetlamy tylko okno: 1 linijka wstecz, aktualna i 3 w przód
            start_idx = max(0, active_idx - 1)
            end_idx = min(len(state.parsed_lyrics), active_idx + 4)

            for i in range(start_idx, end_idx):
                is_active = (i == active_idx)
                text_line = state.parsed_lyrics[i][1]
                if not text_line:
                    text_line = "..." # Przerwa instrumentalna

                lyrics_controls.append(
                    ft.Text(
                        text_line,
                        size=22 if is_active else 15,
                        color=theme.accent if is_active else theme.text_muted,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500,
                        text_align=ft.TextAlign.CENTER,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                )
        else:
            # Zwykły tekst (jeśli API nie miało wersji z czasem)
            lyrics_controls = [ft.Text(state.lyrics_text, color=theme.text_main, size=16, text_align=ft.TextAlign.CENTER)]

        # Kontener wyświetlający linijki
        media_display = ft.Container(
            width=260, height=260,
            bgcolor=theme.panel,
            border_radius=18,
            border=ft.Border(*[ft.BorderSide(1, theme.accent)]*4),
            padding=16,
            content=ft.Column(
                controls=lyrics_controls,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12
            )
        )
    else:
        # Widok okładki albumu
        if state.album_art_url:
            media_display = ft.Image(src=state.album_art_url, width=260, height=260, fit="cover", border_radius=18)
        else:
            # TO JEST TEN BRAKUJĄCY FRAGMENT (SZARA NUTKA PODCZAS ŁADOWANIA)
            media_display = ft.Container(
                width=260, height=260, bgcolor=theme.panel, border_radius=18,
                border=ft.Border(*[ft.BorderSide(1, theme.panel_border)]*4),
                content=ft.Column([
                    ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, size=64, color=theme.text_muted),
                    ft.Text("BLUETOOTH\nAUDIO", size=14, color=theme.text_muted, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_600)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
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

            # Główny interfejs (Okładka po lewej, dane po prawej)
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
