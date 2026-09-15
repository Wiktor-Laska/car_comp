# themes/mazda_night_drive/theme.py
import flet as ft
from core.state import AppState, ThemeId
from core.theme_interface import ThemeInterface, ThemeCallbacks
from themes.mazda_night_drive.home import render_home
from themes.mazda_night_drive.telemetry import render_telemetry
from themes.mazda_night_drive.bluetooth import render_bluetooth
class MazdaNightDriveTheme(ThemeInterface):
    """Mazda Night Drive - minimalistyczny OEM premium."""

    def __init__(self):
        # Paleta zgodna ze specyfikacją
        self.bg = "#0B0D0E"
        self.bg_sec = "#101315"
        self.panel = "#171B1D"
        self.panel_border = "#2A3033"
        self.accent = "#D62828"
        self.text_main = "#F2F4F3"
        self.text_muted = "#626A6D"
        self.danger = "#E53935"
        self.warning = "#F0A83A"

        self.root_stack = None

    def get_root_layout(self, state: AppState, active_screen: ft.Control, callbacks: ThemeCallbacks) -> ft.Control:
        if self.root_stack is None:
            # 1. Główny kontener na ekrany (zostawiamy miejsce na dolny Dock)
            self.screen_container = ft.Container(
                content=active_screen,
                expand=True,
                bgcolor=self.bg,
                padding=ft.Padding(0, 0, 0, 76), # Odstęp na Dock
                alignment=ft.Alignment(0, 0)
            )

            # 2. Permanentny Dock (Bottom Navigation)
            self.dock = self._build_dock(state.active_app, callbacks)

            # 3. Media Bubble (Floating, prawy dolny róg nad dockiem)
            self.media_bubble = ft.Container(
                bgcolor="#181D20",
                border=ft.Border(*[ft.BorderSide(1, "#303639")]*4),
                border_radius=24,
                bottom=96, right=24, # Nad dockiem
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                visible=state.active_app != "bluetooth"
            )
            self._update_media_bubble(state, callbacks)

            # 4. Kamera (Fullscreen popup - radius 0)
            self.camera_view = ft.Container(
                content=ft.Stack([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("REAR CAMERA", size=24, color=self.text_main, weight=ft.FontWeight.BOLD),
                            ft.Text("Symulacja widoku...", size=14, color=self.text_muted)
                        ], alignment="center", horizontal_alignment="center"),
                        expand=True
                    ),
                    ft.Container(
                        content=ft.FloatingActionButton(icon=ft.Icons.CLOSE, bgcolor=self.danger, on_click=lambda _: callbacks["close_camera"]()),
                        top=20, left=20
                    )
                ], expand=True),
                bgcolor=self.bg, expand=True,
                visible=state.is_reverse_engaged or state.is_manual_camera_active
            )

            self.root_stack = ft.Stack([
                self.screen_container,
                self.dock,
                self.media_bubble,
                self.camera_view
            ], expand=True)
        else:
            self.screen_container.content = active_screen
            self.dock.content = self._build_dock(state.active_app, callbacks).content
            self.media_bubble.visible = state.active_app != "bluetooth"
            self._update_media_bubble(state, callbacks)
            self.camera_view.visible = state.is_reverse_engaged or state.is_manual_camera_active

        return self.root_stack

    def _build_dock(self, active_app: str, callbacks: ThemeCallbacks) -> ft.Container:
        def dock_item(icon: ft.IconData, label: str, app_id: str) -> ft.Container:
            is_active = active_app == app_id
            color = self.accent if is_active else self.text_muted
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=28, color=self.text_main if is_active else self.text_muted),
                    ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=color)
                ], alignment="center", horizontal_alignment="center", spacing=4),
                expand=True,
                ink=True,
                bgcolor="#14181A" if is_active else ft.Colors.TRANSPARENT,
                border=ft.Border(top=ft.BorderSide(3, self.accent)) if is_active else None,
                on_click=lambda _: callbacks["navigate"](app_id)
            )

        return ft.Container(
            height=76, bottom=0, left=0, right=0,
            bgcolor=self.bg_sec,
            border=ft.Border(top=ft.BorderSide(1, self.panel_border)),
            content=ft.Row([
                dock_item(ft.Icons.DASHBOARD_ROUNDED, "HOME", "home"),
                dock_item(ft.Icons.ALBUM_ROUNDED, "MEDIA", "bluetooth"),
                dock_item(ft.Icons.RADIO, "RADIO", "radio"),
                dock_item(ft.Icons.SPEED_ROUNDED, "CAR", "telemetry"),
                dock_item(ft.Icons.SETTINGS_ROUNDED, "SETTINGS", "settings"),
            ], spacing=0)
        )

    def _update_media_bubble(self, state: AppState, callbacks: ThemeCallbacks) -> None:
            self.media_bubble.width = 300
            self.media_bubble.height = 62
            # Używamy klasycznego, pancernego ft.Padding(left, top, right, bottom)
            self.media_bubble.padding = ft.Padding(left=8, top=0, right=8, bottom=0)
            self.media_bubble.on_click = lambda _: callbacks["navigate"]("bluetooth")

            self.media_bubble.content = ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, color=self.text_main, size=24),
                    width=46, height=46, bgcolor=self.panel, border_radius=12, alignment=ft.Alignment(0,0)
                ),
                ft.Column([
                    ft.Text(state.current_track_artist, size=13, color=self.text_muted, weight=ft.FontWeight.W_500, max_lines=1),
                    ft.Text(state.current_track_title, size=16, color=self.text_main, weight=ft.FontWeight.BOLD, max_lines=1),
                ], expand=True, alignment="center", spacing=0),
                ft.IconButton(
                    icon=ft.Icons.PAUSE_ROUNDED if state.is_playing else ft.Icons.PLAY_ARROW_ROUNDED,
                    icon_color=self.text_main,
                    on_click=lambda e: (e.control.update(), callbacks["toggle_play"]())
                )
            ], alignment="spaceBetween")
    def render_home_screen(self, navigate_func) -> ft.Control:
        return render_home(self, navigate_func)

    def render_telemetry_screen(self, state: AppState, update_speed_func, update_rpm_func) -> ft.Control:
        return render_telemetry(self, state, update_speed_func, update_rpm_func)

    def render_radio_screen(self, current_station, on_station_change) -> ft.Control:
        return ft.Container(content=ft.Text("RADIO FM - Night Drive", color=self.text_main), alignment=ft.Alignment(0,0))

    def render_bluetooth_screen(self, state, callbacks) -> ft.Control:
        return render_bluetooth(self, state, callbacks)
    def render_settings_screen(self, active_theme_id, on_theme_change) -> ft.Control:
        return ft.Container(content=ft.Text("SETTINGS - Night Drive", color=self.text_main), alignment=ft.Alignment(0,0))
