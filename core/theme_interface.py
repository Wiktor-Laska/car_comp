"""The visual contract that every infotainment theme must satisfy."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypedDict

import flet as ft

from core.state import AppState, ThemeId


NavigationCallback = Callable[[str], None]
ScalarUpdateCallback = Callable[[float], None]
StationChangeCallback = Callable[[str], None]
ThemeChangeCallback = Callable[[ThemeId], None]


class ThemeCallbacks(TypedDict):
    """Controller operations that a root theme layout may invoke."""

    navigate: NavigationCallback
    toggle_media: Callable[[], None]
    close_camera: Callable[[], None]
    toggle_play: Callable[[], None]
    next_track: Callable[[], None]
    prev_track: Callable[[], None]
    connect_bluetooth: Callable[[], None]
    disconnect_bluetooth: Callable[[], None]


class ThemeInterface(ABC):
    """A theme owns all Flet controls; the controller owns only state and events."""

    @abstractmethod
    def get_root_layout(
        self,
        state: AppState,
        active_screen: ft.Control,
        callbacks: ThemeCallbacks,
    ) -> ft.Control:
        """Return the root visual layer, including any global overlays."""

    @abstractmethod
    def render_home_screen(self, navigate_func: NavigationCallback) -> ft.Control:
        """Render the theme's home screen."""

    @abstractmethod
    def render_telemetry_screen(
        self,
        state: AppState,
        update_speed_func: ScalarUpdateCallback,
        update_rpm_func: ScalarUpdateCallback,
    ) -> ft.Control:
        """Render the theme's telemetry screen."""

    @abstractmethod
    def render_radio_screen(
        self,
        current_station: str,
        on_station_change: StationChangeCallback,
    ) -> ft.Control:
        """Render the theme's radio screen."""

    @abstractmethod
    def render_bluetooth_screen(
        self,
        state: AppState,
        callbacks: ThemeCallbacks,
    ) -> ft.Control:
        """Render the theme's Bluetooth audio screen."""

    @abstractmethod
    def render_settings_screen(
        self,
        active_theme_id: ThemeId,
        on_theme_change: ThemeChangeCallback,
    ) -> ft.Control:
        """Render controls that can select the active visual theme."""
