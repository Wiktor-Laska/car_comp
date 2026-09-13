"""Dark Modern visual implementation."""

from __future__ import annotations

import math

import flet as ft
import flet.canvas as cv

from core.state import AppState, ThemeId
from core.theme_interface import (
    NavigationCallback,
    ScalarUpdateCallback,
    StationChangeCallback,
    ThemeCallbacks,
    ThemeChangeCallback,
    ThemeInterface,
)
from themes.dark_modern.bluetooth import build_bluetooth_screen
from themes.dark_modern.settings import build_settings_screen


class DarkModernTheme(ThemeInterface):
    """A clean, contemporary dashboard with persistent overlay controls."""

    def __init__(self) -> None:
        self.bg = "#0b0c10"
        self.panel = "#1f2833"
        self.accent = "#45a29e"
        self.text_main = "#ffffff"
        self.text_muted = "#8b929a"
        self.danger = "#ff4c4c"

        self.root_stack: ft.Stack | None = None
        self.screen_container: ft.Container
        self.home_btn: ft.Container
        self.media_bubble: ft.Container
        self.adas_popup: ft.Container
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
                expand=True,
                bgcolor=self.bg,
                alignment=ft.Alignment(0, 0),
            )
            self.home_btn = ft.Container(
                content=ft.FloatingActionButton(
                    icon=ft.Icons.HOME_ROUNDED,
                    bgcolor=self.panel,
                    on_click=lambda _: callbacks["navigate"]("home"),
                ),
                left=20,
                top=20,
                width=60,
                height=60,
                visible=state.active_app != "home",
            )
            self.media_bubble = ft.Container(
                bgcolor=self.panel,
                padding=10,
                top=20,
                animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT_EXPO),
                visible=state.active_app != "bluetooth",
            )
            self._update_media_bubble(state, callbacks)

            self.adas_popup = ft.Container(
                content=ft.Text("⚠️ Przeszkoda Tył!", color=self.danger),
                bgcolor=self.bg,
                border=ft.Border(*[ft.BorderSide(2, self.danger)] * 4),
                border_radius=10,
                bottom=20,
                right=20,
                width=200,
                height=150,
                alignment=ft.Alignment(0, 0),
                visible=state.is_parking_sensor_active or state.is_reverse_engaged,
            )
            self.camera_view = ft.Container(
                content=ft.Stack(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "WIDEO KAMERY COFANIA",
                                        size=30,
                                        color=self.text_main,
                                    ),
                                    ft.Text(
                                        "(Symulacja z motywu Dark Modern)",
                                        size=14,
                                        color=self.text_muted,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            alignment=ft.Alignment(0, 0),
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.FloatingActionButton(
                                icon=ft.Icons.CLOSE,
                                bgcolor=self.danger,
                                on_click=lambda _: callbacks["close_camera"](),
                            ),
                            left=20,
                            top=20,
                        ),
                    ],
                    expand=True,
                ),
                bgcolor=self.bg,
                expand=True,
                visible=state.is_reverse_engaged or state.is_manual_camera_active,
            )
            self.root_stack = ft.Stack(
                [
                    self.screen_container,
                    self.home_btn,
                    self.media_bubble,
                    self.camera_view,
                    self.adas_popup,
                ],
                expand=True,
            )
        else:
            self.screen_container.content = active_screen
            self.home_btn.visible = state.active_app != "home"
            self.media_bubble.visible = state.active_app != "bluetooth"
            self._update_media_bubble(state, callbacks)
            self.adas_popup.visible = (
                state.is_parking_sensor_active or state.is_reverse_engaged
            )
            self.camera_view.visible = (
                state.is_reverse_engaged or state.is_manual_camera_active
            )

        assert self.root_stack is not None
        return self.root_stack

    def _update_media_bubble(
        self,
        state: AppState,
        callbacks: ThemeCallbacks,
    ) -> None:
        is_expanded = state.is_media_expanded
        self.media_bubble.width = 330 if is_expanded else 50
        self.media_bubble.height = 90 if is_expanded else 60
        self.media_bubble.right = 20 if is_expanded else 0
        self.media_bubble.border_radius = (
            ft.BorderRadius(15, 15, 15, 15)
            if is_expanded
            else ft.BorderRadius(15, 0, 15, 0)
        )
        self.media_bubble.on_click = (
            None
            if is_expanded
            else lambda _: callbacks["toggle_media"]()
        )

        if is_expanded:
            self.media_bubble.content = ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.ALBUM,
                            size=40,
                            color=self.text_main,
                        ),
                        width=60,
                        height=60,
                        bgcolor=self.bg,
                        border_radius=10,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                state.current_track_title,
                                color=self.text_main,
                                weight=ft.FontWeight.BOLD,
                                size=16,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                state.current_track_artist,
                                color=self.text_muted,
                                size=12,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=(
                            ft.Icons.PAUSE_ROUNDED
                            if state.is_playing
                            else ft.Icons.PLAY_ARROW_ROUNDED
                        ),
                        icon_color=self.accent,
                        tooltip="Wstrzymaj" if state.is_playing else "Odtwórz",
                        disabled=not state.bt_connected,
                        on_click=lambda _: callbacks["toggle_play"](),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_RIGHT,
                        icon_color=self.text_muted,
                        on_click=lambda _: callbacks["toggle_media"](),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            self.media_bubble.content = ft.Icon(
                ft.Icons.KEYBOARD_ARROW_LEFT,
                color=self.text_muted,
            )

    def render_home_screen(self, navigate_func: NavigationCallback) -> ft.Control:
        def make_tile(
            title: str,
            icon: ft.IconData,
            app_id: str,
            color_accent: str | None = None,
        ) -> ft.Container:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon, size=60, color=color_accent or self.accent),
                        ft.Text(title, color=self.text_main),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=160,
                height=160,
                bgcolor=self.panel,
                border_radius=20,
                ink=True,
                on_click=lambda _: navigate_func(app_id),
            )

        return ft.Container(
            content=ft.Row(
                controls=[
                    make_tile("Radio", ft.Icons.RADIO, "radio"),
                    make_tile("Bluetooth", ft.Icons.BLUETOOTH, "bluetooth"),
                    make_tile("Telemetria", ft.Icons.SPEED, "telemetry"),
                    make_tile("Ustawienia", ft.Icons.SETTINGS, "settings"),
                    make_tile("Kamera", ft.Icons.CAMERA_ALT, "manual_camera"),
                    make_tile(
                        "Wsteczny",
                        ft.Icons.CAR_CRASH,
                        "reverse_test",
                        color_accent=self.danger,
                    ),
                ],
                wrap=True,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=ft.Padding(left=50, top=100, right=50, bottom=0),
            expand=True,
        )

    def render_telemetry_screen(
        self,
        state: AppState,
        update_speed_func: ScalarUpdateCallback,
        update_rpm_func: ScalarUpdateCallback,
    ) -> ft.Control:
        class CircularGauge(ft.Container):
            def __init__(
                self,
                title: str,
                max_value: float,
                current_value: float,
                redline_start: float,
            ) -> None:
                super().__init__()
                self.max_value = max_value
                self.redline_start = redline_start
                self.value_text = ft.Text(
                    str(int(current_value)),
                    size=50,
                    color=self_outer.accent,
                    weight=ft.FontWeight.BOLD,
                )
                self.title_text = ft.Text(title, size=16, color=self_outer.accent)
                self.value_arc = cv.Arc(
                    x=10,
                    y=10,
                    width=230,
                    height=230,
                    start_angle=0.75 * math.pi,
                    sweep_angle=self._sweep_angle(current_value),
                    paint=ft.Paint(
                        color=self_outer.accent,
                        stroke_width=15,
                        style=ft.PaintingStyle.STROKE,
                        stroke_cap=ft.StrokeCap.ROUND,
                    ),
                )
                background_arc = cv.Arc(
                    x=10,
                    y=10,
                    width=230,
                    height=230,
                    start_angle=0.75 * math.pi,
                    sweep_angle=1.5 * math.pi,
                    paint=ft.Paint(
                        color=self_outer.panel,
                        stroke_width=15,
                        style=ft.PaintingStyle.STROKE,
                        stroke_cap=ft.StrokeCap.ROUND,
                    ),
                )
                self.content = ft.Stack(
                    [
                        cv.Canvas([background_arc, self.value_arc], width=250, height=250),
                        ft.Container(
                            content=ft.Column(
                                [self.value_text, self.title_text],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0,
                            ),
                            width=250,
                            height=250,
                            alignment=ft.Alignment(0, 0),
                        ),
                    ],
                    width=250,
                    height=250,
                )

            def _sweep_angle(self, value: float) -> float:
                bounded_value = max(0.0, min(value, self.max_value))
                return max(0.01, (bounded_value / self.max_value) * (1.5 * math.pi))

            def update_value(self, value: float) -> None:
                bounded_value = max(0.0, min(value, self.max_value))
                is_danger = bounded_value >= self.redline_start
                color = self_outer.danger if is_danger else self_outer.accent
                self.value_text.value = str(int(bounded_value))
                self.value_arc.sweep_angle = self._sweep_angle(bounded_value)
                self.value_arc.paint.color = color
                self.value_text.color = color
                self.title_text.color = color
                self.update()

        self_outer = self
        speed_gauge = CircularGauge("km/h", 240.0, state.speed, 140.0)
        rpm_gauge = CircularGauge("RPM", 8000.0, state.rpm, 6500.0)

        def on_speed(event: ft.ControlEvent) -> None:
            value = float(event.control.value)
            update_speed_func(value)
            speed_gauge.update_value(value)

        def on_rpm(event: ft.ControlEvent) -> None:
            value = float(event.control.value)
            update_rpm_func(value)
            rpm_gauge.update_value(value)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [speed_gauge, rpm_gauge],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=80,
                    ),
                    ft.Container(height=40),
                    ft.Row(
                        [
                            ft.Slider(
                                min=0,
                                max=240,
                                value=state.speed,
                                on_change=on_speed,
                                width=250,
                                active_color=self.accent,
                            ),
                            ft.Slider(
                                min=0,
                                max=8000,
                                value=state.rpm,
                                on_change=on_rpm,
                                width=250,
                                active_color=self.accent,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=60,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

    def render_radio_screen(
        self,
        current_station: str,
        on_station_change: StationChangeCallback,
    ) -> ft.Control:
        def build_preset_button(frequency: str) -> ft.ElevatedButton:
            return ft.ElevatedButton(
                content=ft.Text(
                    f"{frequency} FM",
                    color=self.text_main,
                    weight=ft.FontWeight.BOLD,
                ),
                style=ft.ButtonStyle(
                    bgcolor=self.panel,
                    side=(
                        ft.BorderSide(2, self.accent)
                        if current_station == frequency
                        else None
                    ),
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=20,
                ),
                on_click=lambda _: on_station_change(frequency),
            )

        def on_slider_change(event: ft.ControlEvent) -> None:
            on_station_change(f"{float(event.control.value):.1f}")

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.RADIO, size=80, color=self.accent),
                    ft.Text(
                        f"{current_station} MHz",
                        size=70,
                        weight=ft.FontWeight.BOLD,
                        color=self.text_main,
                    ),
                    ft.Text("RADIO FM", size=18, color=self.text_muted),
                    ft.Container(height=40),
                    ft.Slider(
                        min=87.5,
                        max=108.0,
                        value=float(current_station),
                        divisions=205,
                        label="{value} MHz",
                        on_change=on_slider_change,
                        active_color=self.accent,
                        inactive_color=self.text_muted,
                        width=600,
                    ),
                    ft.Container(height=30),
                    ft.Row(
                        controls=[
                            build_preset_button("89.8"),
                            build_preset_button("93.3"),
                            build_preset_button("104.4"),
                            build_preset_button("107.5"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

    def render_bluetooth_screen(
        self,
        state: AppState,
        callbacks: ThemeCallbacks,
    ) -> ft.Control:
        return build_bluetooth_screen(
            theme=self,
            state=state,
            callbacks=callbacks,
        )

    def render_settings_screen(
        self,
        active_theme_id: ThemeId,
        on_theme_change: ThemeChangeCallback,
    ) -> ft.Control:
        return build_settings_screen(
            active_theme_id=active_theme_id,
            on_theme_change=on_theme_change,
            background_color=self.bg,
            panel_color=self.panel,
            accent_color=self.accent,
            text_color=self.text_main,
            muted_text_color=self.text_muted,
        )
