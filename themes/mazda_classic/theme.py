"""Retro-inspired Mazda Classic theme implementation.

This intentionally uses a different component hierarchy from Dark Modern: the
home screen is a vertical menu and telemetry uses rectangular digital readouts.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from core.state import AppState, ThemeId
from core.theme_interface import (
    NavigationCallback,
    ScalarUpdateCallback,
    StationChangeCallback,
    ThemeCallbacks,
    ThemeChangeCallback,
    ThemeInterface,
)


class MazdaClassicTheme(ThemeInterface):
    """A high-contrast dashboard inspired by early Mazda head units."""

    def __init__(self) -> None:
        self.bg = "#050505"
        self.panel = "#16110f"
        self.panel_highlight = "#251512"
        self.accent = "#ff3300"
        self.accent_dim = "#8f220e"
        self.text_main = "#fff0e8"
        self.text_muted = "#b59a90"
        self.danger = "#ff5a36"

        self.root_stack: ft.Stack | None = None
        self.screen_container: ft.Container
        self.home_button: ft.Container
        self.media_panel: ft.Container
        self.camera_view: ft.Container

    def get_root_layout(
        self,
        state: AppState,
        active_screen: ft.Control,
        callbacks: ThemeCallbacks,
    ) -> ft.Control:
        if self.root_stack is None:
            self.screen_container = ft.Container(
                content=active_screen,
                bgcolor=self.bg,
                expand=True,
            )
            self.home_button = ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.HOME,
                    icon_color=self.accent,
                    tooltip="Menu główne",
                    on_click=lambda _: callbacks["navigate"]("home"),
                ),
                left=18,
                top=18,
                bgcolor=self.panel,
                border=ft.Border(*[ft.BorderSide(1, self.accent_dim)] * 4),
                border_radius=4,
                visible=state.active_app != "home",
            )
            self.media_panel = ft.Container(
                right=20,
                bottom=18,
                bgcolor=self.panel,
                border=ft.Border(*[ft.BorderSide(1, self.accent_dim)] * 4),
                border_radius=4,
            )
            self._update_media_panel(state, callbacks)
            self.camera_view = ft.Container(
                expand=True,
                bgcolor="#000000",
                visible=state.is_reverse_engaged or state.is_manual_camera_active,
                content=ft.Stack(
                    [
                        ft.Container(
                            expand=True,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "KAMERA COFANIA",
                                        color=self.accent,
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Container(
                                        width=620,
                                        height=260,
                                        bgcolor="#171717",
                                        border=ft.Border(
                                            ft.BorderSide(2, self.accent),
                                            ft.BorderSide(2, self.accent),
                                            ft.BorderSide(2, self.accent),
                                            ft.BorderSide(2, self.accent),
                                        ),
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Text(
                                            "SYGNAŁ WIDEO",
                                            color=self.text_muted,
                                            size=18,
                                        ),
                                    ),
                                ],
                                tight=True,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ),
                        ft.Container(
                            top=20,
                            left=20,
                            content=ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_color=self.text_main,
                                bgcolor=self.accent,
                                on_click=lambda _: callbacks["close_camera"](),
                            ),
                        ),
                    ],
                    expand=True,
                ),
            )
            self.root_stack = ft.Stack(
                [
                    self.screen_container,
                    self.home_button,
                    self.media_panel,
                    self.camera_view,
                ],
                expand=True,
            )
        else:
            self.screen_container.content = active_screen
            self.home_button.visible = state.active_app != "home"
            self._update_media_panel(state, callbacks)
            self.camera_view.visible = (
                state.is_reverse_engaged or state.is_manual_camera_active
            )

        assert self.root_stack is not None
        return self.root_stack

    def _update_media_panel(
        self,
        state: AppState,
        callbacks: ThemeCallbacks,
    ) -> None:
        self.media_panel.width = 320 if state.is_media_expanded else 64
        self.media_panel.height = 58
        self.media_panel.padding = 8
        self.media_panel.on_click = (
            None
            if state.is_media_expanded
            else lambda _: callbacks["toggle_media"]()
        )
        if state.is_media_expanded:
            self.media_panel.content = ft.Row(
                [
                    ft.Icon(ft.Icons.MUSIC_NOTE, color=self.accent),
                    ft.Text(
                        "AUX  •  TRACK 01",
                        color=self.text_main,
                        weight=ft.FontWeight.BOLD,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                        icon_color=self.accent,
                        on_click=lambda _: callbacks["toggle_media"](),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            self.media_panel.content = ft.Icon(
                ft.Icons.KEYBOARD_ARROW_UP,
                color=self.accent,
            )

    def render_home_screen(self, navigate_func: NavigationCallback) -> ft.Control:
        def menu_item(
            icon: ft.IconData,
            title: str,
            subtitle: str,
            app_id: str,
            *,
            highlight: bool = False,
        ) -> ft.Container:
            item_color = self.danger if highlight else self.accent
            return ft.Container(
                width=680,
                padding=ft.Padding(left=24, top=14, right=18, bottom=14),
                bgcolor=self.panel_highlight if highlight else self.panel,
                border=ft.Border(
                    ft.BorderSide(1, self.accent_dim),
                    ft.BorderSide(1, self.accent_dim),
                    ft.BorderSide(1, self.accent_dim),
                    ft.BorderSide(3, item_color),
                ),
                ink=True,
                on_click=lambda _: navigate_func(app_id),
                content=ft.Row(
                    [
                        ft.Icon(icon, size=34, color=item_color),
                        ft.Column(
                            [
                                ft.Text(
                                    title.upper(),
                                    color=self.text_main,
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(subtitle, color=self.text_muted, size=13),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                        ft.Icon(
                            ft.Icons.CHEVRON_RIGHT,
                            color=item_color,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

        return ft.Container(
            expand=True,
            padding=ft.Padding(left=0, top=60, right=0, bottom=50),
            content=ft.Column(
                [
                    ft.Text(
                        "MAZDA 6  •  SYSTEM AUDIO",
                        color=self.accent,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(width=680, height=2, bgcolor=self.accent),
                    menu_item(
                        ft.Icons.RADIO,
                        "Radio FM",
                        "Tuner i zapisane stacje",
                        "radio",
                    ),
                    menu_item(
                        ft.Icons.SPEED,
                        "Telemetria",
                        "Prędkość i obroty silnika",
                        "telemetry",
                    ),
                    menu_item(
                        ft.Icons.BLUETOOTH,
                        "Bluetooth Audio",
                        "Odtwarzanie muzyki z telefonu",
                        "bluetooth",
                    ),
                    menu_item(
                        ft.Icons.SETTINGS,
                        "Ustawienia",
                        "Wygląd oraz ustawienia systemu",
                        "settings",
                    ),
                    menu_item(
                        ft.Icons.CAMERA_ALT,
                        "Kamera",
                        "Podgląd kamery",
                        "manual_camera",
                    ),
                    menu_item(
                        ft.Icons.CAR_CRASH,
                        "Test biegu wstecznego",
                        "Symulacja kamery i czujników",
                        "reverse_test",
                        highlight=True,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

    def render_telemetry_screen(
        self,
        state: AppState,
        update_speed_func: ScalarUpdateCallback,
        update_rpm_func: ScalarUpdateCallback,
    ) -> ft.Control:
        speed_value = ft.Text(
            f"{state.speed:03.0f}",
            size=88,
            color=self.accent,
            weight=ft.FontWeight.BOLD,
        )
        rpm_value = ft.Text(
            f"{state.rpm:04.0f}",
            size=88,
            color=self.accent,
            weight=ft.FontWeight.BOLD,
        )

        def readout(label: str, value: ft.Text, unit: str) -> ft.Container:
            return ft.Container(
                width=340,
                padding=22,
                bgcolor="#000000",
                border=ft.Border(*[ft.BorderSide(2, self.accent_dim)] * 4),
                content=ft.Column(
                    [
                        ft.Text(label, color=self.text_muted, size=16),
                        ft.Row(
                            [
                                value,
                                ft.Text(
                                    unit,
                                    color=self.text_main,
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

        def on_speed(event: ft.ControlEvent) -> None:
            value = float(event.control.value)
            update_speed_func(value)
            speed_value.value = f"{value:03.0f}"
            speed_value.update()

        def on_rpm(event: ft.ControlEvent) -> None:
            value = float(event.control.value)
            update_rpm_func(value)
            rpm_value.value = f"{value:04.0f}"
            rpm_value.color = self.danger if value >= 6500 else self.accent
            rpm_value.update()

        return ft.Container(
            expand=True,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                [
                    ft.Text(
                        "INSTRUMENT CLUSTER",
                        color=self.text_main,
                        size=25,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        [
                            readout("PRĘDKOŚĆ", speed_value, "km/h"),
                            readout("OBROTY SILNIKA", rpm_value, "rpm"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=28,
                    ),
                    ft.Container(width=708, height=2, bgcolor=self.accent),
                    ft.Row(
                        [
                            ft.Slider(
                                min=0,
                                max=240,
                                value=state.speed,
                                width=340,
                                active_color=self.accent,
                                inactive_color=self.accent_dim,
                                on_change=on_speed,
                            ),
                            ft.Slider(
                                min=0,
                                max=8000,
                                value=state.rpm,
                                width=340,
                                active_color=self.accent,
                                inactive_color=self.accent_dim,
                                on_change=on_rpm,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=24,
            ),
        )

    def render_radio_screen(
        self,
        current_station: str,
        on_station_change: StationChangeCallback,
    ) -> ft.Control:
        def preset_button(frequency: str) -> ft.OutlinedButton:
            is_selected = frequency == current_station
            return ft.OutlinedButton(
                content=ft.Text(
                    frequency,
                    color=self.text_main,
                    weight=ft.FontWeight.BOLD,
                ),
                style=ft.ButtonStyle(
                    side=ft.BorderSide(2, self.accent if is_selected else self.accent_dim),
                    bgcolor=self.panel_highlight if is_selected else self.panel,
                    shape=ft.RoundedRectangleBorder(radius=3),
                    padding=18,
                ),
                on_click=lambda _: on_station_change(frequency),
            )

        def on_slider_change(event: ft.ControlEvent) -> None:
            on_station_change(f"{float(event.control.value):.1f}")

        return ft.Container(
            expand=True,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                [
                    ft.Text("MAZDA FM TUNER", color=self.text_muted, size=19),
                    ft.Container(
                        width=560,
                        padding=20,
                        bgcolor="#000000",
                        border=ft.Border(*[ft.BorderSide(2, self.accent)] * 4),
                        content=ft.Text(
                            f"{current_station} MHz",
                            color=self.accent,
                            size=74,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                    ft.Slider(
                        min=87.5,
                        max=108.0,
                        value=float(current_station),
                        divisions=205,
                        label="{value} MHz",
                        width=560,
                        active_color=self.accent,
                        inactive_color=self.accent_dim,
                        on_change=on_slider_change,
                    ),
                    ft.Row(
                        [
                            preset_button("89.8"),
                            preset_button("93.3"),
                            preset_button("104.4"),
                            preset_button("107.5"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=24,
            ),
        )

    def render_bluetooth_screen(
        self,
        state: AppState,
        callbacks: ThemeCallbacks,
    ) -> ft.Control:
        """Render a compact retro Bluetooth player for interface compatibility."""
        maximum_progress = max(state.track_duration_seconds, 1.0)
        progress = min(max(state.track_elapsed_seconds, 0.0), maximum_progress)
        play_icon = (
            ft.Icons.PAUSE_ROUNDED
            if state.is_playing
            else ft.Icons.PLAY_ARROW_ROUNDED
        )

        def control_button(
            icon: ft.IconData,
            tooltip: str,
            callback: Callable[[], None],
            *,
            primary: bool = False,
        ) -> ft.IconButton:
            return ft.IconButton(
                icon=icon,
                icon_size=42 if primary else 32,
                icon_color=self.bg if primary else self.accent,
                bgcolor=self.accent if primary else self.panel,
                tooltip=tooltip,
                disabled=not state.bt_connected,
                on_click=lambda _: callback(),
            )

        return ft.Container(
            expand=True,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                (
                                    ft.Icons.BLUETOOTH_CONNECTED
                                    if state.bt_connected
                                    else ft.Icons.BLUETOOTH_DISABLED
                                ),
                                color=self.accent,
                            ),
                            ft.Text(
                                state.bt_status_message,
                                color=self.text_muted,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.OutlinedButton(
                                content=ft.Text(
                                    "ROZŁĄCZ" if state.bt_connected else "POŁĄCZ",
                                    color=self.accent,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                style=ft.ButtonStyle(
                                    side=ft.BorderSide(1, self.accent),
                                    shape=ft.RoundedRectangleBorder(radius=3),
                                ),
                                on_click=lambda _: (
                                    callbacks["disconnect_bluetooth"]()
                                    if state.bt_connected
                                    else callbacks["connect_bluetooth"]()
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        width=220,
                        height=220,
                        bgcolor="#000000",
                        border=ft.Border(*[ft.BorderSide(2, self.accent)] * 4),
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(
                            ft.Icons.ALBUM_ROUNDED,
                            color=self.accent,
                            size=112,
                        ),
                    ),
                    ft.Text(
                        state.current_track_title,
                        color=self.text_main,
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        state.current_track_artist,
                        color=self.text_muted,
                        size=17,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Slider(
                        min=0,
                        max=maximum_progress,
                        value=progress,
                        width=560,
                        active_color=self.accent,
                        inactive_color=self.accent_dim,
                        disabled=True,
                    ),
                    ft.Row(
                        [
                            control_button(
                                ft.Icons.SKIP_PREVIOUS_ROUNDED,
                                "Poprzedni utwór",
                                callbacks["prev_track"],
                            ),
                            control_button(
                                play_icon,
                                "Wstrzymaj" if state.is_playing else "Odtwórz",
                                callbacks["toggle_play"],
                                primary=True,
                            ),
                            control_button(
                                ft.Icons.SKIP_NEXT_ROUNDED,
                                "Następny utwór",
                                callbacks["next_track"],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=24,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
        )

    def render_settings_screen(
        self,
        active_theme_id: ThemeId,
        on_theme_change: ThemeChangeCallback,
    ) -> ft.Control:
        target_theme: ThemeId = (
            "dark_modern" if active_theme_id == "mazda_classic" else "mazda_classic"
        )
        return ft.Container(
            expand=True,
            alignment=ft.Alignment(0, 0),
            content=ft.Container(
                width=620,
                padding=30,
                bgcolor=self.panel,
                border=ft.Border(*[ft.BorderSide(2, self.accent_dim)] * 4),
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.SETTINGS, size=58, color=self.accent),
                        ft.Text(
                            "USTAWIENIA SYSTEMU",
                            color=self.text_main,
                            size=26,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "WYGLĄD: MAZDA CLASSIC",
                            color=self.text_muted,
                            size=15,
                        ),
                        ft.Container(width=500, height=1, bgcolor=self.accent_dim),
                        ft.OutlinedButton(
                            content=ft.Text(
                                "PRZEŁĄCZ NA DARK MODERN",
                                color=self.text_main,
                                weight=ft.FontWeight.BOLD,
                            ),
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(2, self.accent),
                                shape=ft.RoundedRectangleBorder(radius=3),
                                padding=ft.Padding(
                                    left=24,
                                    top=18,
                                    right=24,
                                    bottom=18,
                                ),
                            ),
                            on_click=lambda _: on_theme_change(target_theme),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
            ),
        )
