"""Application data that is independent from any Flet layout."""

from dataclasses import dataclass
from typing import Literal, TypeAlias


ThemeId: TypeAlias = Literal["dark_modern", "mazda_classic", "mazda_night_drive"]
BluetoothConnectionState: TypeAlias = Literal[
    "unavailable",
    "disconnected",
    "connecting",
    "connected",
    "error",
]


@dataclass(slots=True)
class AppState:
    """Mutable runtime state shared by the controller and the active theme."""

    active_app: str = "home"
    theme_id: ThemeId = "mazda_night_drive"

    is_media_expanded: bool = True
    is_reverse_engaged: bool = False
    is_parking_sensor_active: bool = False
    is_manual_camera_active: bool = False

    speed: float = 0.0
    rpm: float = 0.0
    current_radio_station: str = "104.4"

    # Bluetooth audio state. These values will later be supplied by the
    # BlueZ/media-service integration running on the Raspberry Pi.
    bt_connected: bool = False
    bt_device_name: str = "Pixel 8 Pro"
    bt_device_address: str = ""
    bt_connection_state: BluetoothConnectionState = "disconnected"
    bt_status_message: str = "Bluetooth gotowy do połączenia"
    is_playing: bool = False
    current_track_title: str = "Alone"
    current_track_artist: str = "I Prevail"
    track_elapsed_seconds: float = 86.0
    track_duration_seconds: float = 232.0
    bt_playlist_index: int = 0

    # NOWE ZMIENNE DO MUZYKI:
    album_art_url: str | None = None
    lyrics_text: str = "Szukam tekstu w sieci...\n\n(Symulacja pobierania z API LRCLIB)"
    is_lyrics_visible: bool = False
