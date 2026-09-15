"""Application controller for the Mazda infotainment prototype.

This module intentionally creates no visual controls. It coordinates pure
application state with whichever theme is currently active.
"""

import asyncio
import os
from collections.abc import Awaitable, Callable, Mapping
from typing import TypeAlias

import flet as ft

from core.state import AppState, ThemeId
from core.bluetooth_service import BluetoothMediaService, BluetoothServiceError
from core.theme_interface import ThemeCallbacks, ThemeInterface
from themes.dark_modern.theme import DarkModernTheme
from themes.mazda_classic.theme import MazdaClassicTheme
from themes.mazda_night_drive.theme import MazdaNightDriveTheme

ThemeFactory = Callable[[], ThemeInterface]
MockTrack: TypeAlias = tuple[str, str, float]
BluetoothOperation: TypeAlias = Callable[[AppState], Awaitable[None]]

THEME_FACTORIES: Mapping[ThemeId, ThemeFactory] = {
    "dark_modern": DarkModernTheme,
    "mazda_classic": MazdaClassicTheme,
    "mazda_night_drive": MazdaNightDriveTheme,
}
MOCK_BLUETOOTH_PLAYLIST: tuple[MockTrack, ...] = (
    ("Alone", "I Prevail", 232.0),
    ("The Pretender", "Foo Fighters", 269.0),
    ("In the End", "Linkin Park", 216.0),
)


class AppController:
    """Owns app state, event handlers, and the active theme instance."""

    def __init__(
        self,
        page: ft.Page,
        theme_factories: Mapping[ThemeId, ThemeFactory],
    ) -> None:
        self.page = page
        self.state = AppState()
        self._theme_factories = dict(theme_factories)
        self.theme = self._create_theme(self.state.theme_id)
        self._bluetooth_service = BluetoothMediaService(
            preferred_device_address=os.environ.get("MAZDA_BT_DEVICE_ADDRESS", "")
        )
        self._uses_bluez = self._bluetooth_service.is_supported_host()

        self.page.padding = 0
        self.page.bgcolor = ft.Colors.TRANSPARENT

        self.callbacks: ThemeCallbacks = {
            "navigate": self.navigate,
            "toggle_media": self.toggle_media,
            "close_camera": self.close_camera,
            "toggle_play": self.toggle_play,
            "next_track": self.next_track,
            "prev_track": self.prev_track,
            "connect_bluetooth": self.connect_bluetooth,
            "disconnect_bluetooth": self.disconnect_bluetooth,
            "toggle_lyrics": self.toggle_lyrics,
        }
        self.update_ui(replace_root_layout=True)

        if self._uses_bluez:
            self.page.run_task(self._initialize_bluetooth)
        else:
            self.state.bt_connection_state = "unavailable"
            self.state.bt_status_message = "BlueZ działa wyłącznie na Raspberry Pi OS"
            self.update_ui()

    def _create_theme(self, theme_id: ThemeId) -> ThemeInterface:
        """Build a fresh theme so it cannot retain controls from another theme."""
        return self._theme_factories[theme_id]()

    def update_ui(self, *, replace_root_layout: bool = False) -> None:
        """Render the active screen through the current theme.

        A theme swap requires replacing the page root: each theme owns a
        different Flet control tree and may keep references to its overlays.
        """
        current_title = self.state.current_track_title
            # Wykrywamy, czy iPhone przesłał właśnie nowy tytuł
        if getattr(self, '_last_seen_title', None) != current_title:
            self._last_seen_title = current_title
            if current_title and current_title != "Unknown":
                # Generujemy obrazek na podstawie prawdziwego tytułu z BT
                safe_title = current_title.replace(" ", "").replace("/", "")
                self.state.album_art_url = f"https://picsum.photos/seed/{safe_title}/300/300"
                self.state.lyrics_text = f"Odtwarzasz z telefonu:\n{current_title}\n\n[Trwa szukanie tekstu online...]"
            else:
                self.state.album_art_url = None
        active_screen = self._get_active_screen()
        layout = self.theme.get_root_layout(self.state, active_screen, self.callbacks)

        if replace_root_layout or not self.page.controls:
            self.page.controls.clear()
            self.page.add(layout)
            return

        self.page.update()

    def navigate(self, app_id: str) -> None:
        """Handle a request to display an application or a camera overlay."""
        if app_id == "manual_camera":
            self.state.is_manual_camera_active = True
        elif app_id == "reverse_test":
            self.state.is_reverse_engaged = not self.state.is_reverse_engaged
        else:
            self.state.active_app = app_id

        self.update_ui()

    def toggle_media(self) -> None:
        self.state.is_media_expanded = not self.state.is_media_expanded
        self.update_ui()

    def close_camera(self) -> None:
        self.state.is_manual_camera_active = False
        self.state.is_reverse_engaged = False
        self.update_ui()

    def toggle_play(self) -> None:
        """Toggle real AVRCP playback, or use mock state outside the Pi target."""
        if self._uses_bluez:
            self._run_bluetooth_operation(self._bluetooth_service.toggle_playback)
            return

        self.state.is_playing = not self.state.is_playing
        self.update_ui()
    def toggle_lyrics(self) -> None:
            self.state.is_lyrics_visible = not self.state.is_lyrics_visible
            self.update_ui()
    def next_track(self) -> None:
        """Request the next AVRCP track, with a desktop mock fallback."""
        if self._uses_bluez:
            self._run_bluetooth_operation(self._bluetooth_service.next_track)
            return

        next_index = (self.state.bt_playlist_index + 1) % len(
            MOCK_BLUETOOTH_PLAYLIST
        )
        self._select_bluetooth_track(next_index)
        self.update_ui()

    def prev_track(self) -> None:
        """Request the previous AVRCP track, with a desktop mock fallback."""
        if self._uses_bluez:
            self._run_bluetooth_operation(self._bluetooth_service.previous_track)
            return

        previous_index = (self.state.bt_playlist_index - 1) % len(
            MOCK_BLUETOOTH_PLAYLIST
        )
        self._select_bluetooth_track(previous_index)
        self.update_ui()

    def _select_bluetooth_track(self, track_index: int) -> None:
        """Apply a mock track as a single state transaction."""
        title, artist, duration_seconds = MOCK_BLUETOOTH_PLAYLIST[track_index]
        self.state.bt_playlist_index = track_index
        self.state.current_track_title = title
        self.state.current_track_artist = artist
        self.state.track_elapsed_seconds = 0.0
        self.state.track_duration_seconds = duration_seconds
        self.state.is_playing = True
        safe_title = title.replace(" ", "")
        self.state.album_art_url = f"https://picsum.photos/seed/{safe_title}/300/300"

        # Symulacja tekstu piosenki
        self.state.lyrics_text = f"Odtwarzasz utwór:\n{title}\nwykonawcy: {artist}\n\nTekst zsynchronizowany:\n[00:10] ...śpiewanie...\n[00:20] ...refren...\n[00:45] (Gitara gra)\n\nSystem Mazda Pulse UI v1.0"
    def connect_bluetooth(self) -> None:
        """Connect the paired phone selected by the Pi Bluetooth configuration."""
        if not self._uses_bluez:
            self.state.bt_connection_state = "unavailable"
            self.state.bt_status_message = "Połączenie Bluetooth wymaga Raspberry Pi OS"
            self.update_ui()
            return

        self.state.bt_connection_state = "connecting"
        self.state.bt_status_message = "Łączenie Bluetooth…"
        self.update_ui()
        self._run_bluetooth_operation(self._bluetooth_service.connect_saved_device)

    def disconnect_bluetooth(self) -> None:
        """Disconnect the currently selected Bluetooth phone."""
        if not self._uses_bluez:
            return
        self._run_bluetooth_operation(self._bluetooth_service.disconnect_device)

    def _run_bluetooth_operation(self, operation: BluetoothOperation) -> None:
        """Schedule slow BlueZ I/O outside Flet's synchronous event callback."""
        self.page.run_task(self._execute_bluetooth_operation, operation)

    async def _initialize_bluetooth(self) -> None:
        """Start BlueZ integration and poll its media properties on the Pi."""
        try:
            await self._bluetooth_service.refresh_state(self.state)
        except BluetoothServiceError as error:
            self.state.bt_connection_state = "error"
            self.state.bt_status_message = str(error)
            self.update_ui()
            return

        self.update_ui()
        await self._monitor_bluetooth_state()

    async def _monitor_bluetooth_state(self) -> None:
        """Keep track metadata and progress current without blocking the UI."""
        while True:
            await asyncio.sleep(1.0)
            try:
                state_changed = await self._bluetooth_service.refresh_state(self.state)
            except BluetoothServiceError as error:
                self.state.bt_connection_state = "error"
                self.state.bt_status_message = str(error)
                self.update_ui()
                return

            if state_changed:
                self.update_ui()

    async def _execute_bluetooth_operation(
        self,
        operation: BluetoothOperation,
    ) -> None:
        try:
            await operation(self.state)
        except BluetoothServiceError as error:
            self.state.bt_connection_state = "error"
            self.state.bt_status_message = str(error)
        self.update_ui()

    def update_speed(self, value: float) -> None:
        """Store live speed without rebuilding the full control tree."""
        self.state.speed = value

    def update_rpm(self, value: float) -> None:
        """Store live engine speed without rebuilding the full control tree."""
        self.state.rpm = value

    def set_radio_station(self, frequency: str) -> None:
        self.state.current_radio_station = frequency
        self.update_ui()

    def switch_theme(self, theme_id: ThemeId) -> None:
        """Swap visual implementations while retaining all application data."""
        if theme_id == self.state.theme_id:
            return

        self.state.theme_id = theme_id
        self.theme = self._create_theme(theme_id)
        self.update_ui(replace_root_layout=True)

    def _get_active_screen(self) -> ft.Control:
        if self.state.active_app == "home":
            return self.theme.render_home_screen(navigate_func=self.navigate)

        if self.state.active_app == "telemetry":
            return self.theme.render_telemetry_screen(
                state=self.state,
                update_speed_func=self.update_speed,
                update_rpm_func=self.update_rpm,
            )

        if self.state.active_app == "radio":
            return self.theme.render_radio_screen(
                current_station=self.state.current_radio_station,
                on_station_change=self.set_radio_station,
            )

        if self.state.active_app == "bluetooth":
            return self.theme.render_bluetooth_screen(
                state=self.state,
                callbacks=self.callbacks,
            )

        if self.state.active_app == "settings":
            return self.theme.render_settings_screen(
                active_theme_id=self.state.theme_id,
                on_theme_change=self.switch_theme,
            )

        # Unknown application identifiers fall back to Home without creating UI here.
        self.state.active_app = "home"
        return self.theme.render_home_screen(navigate_func=self.navigate)


def main(page: ft.Page) -> None:
    AppController(page, theme_factories=THEME_FACTORIES)


if __name__ == "__main__":
    ft.run(main)
