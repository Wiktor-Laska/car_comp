"""Asynchronous BlueZ integration for Raspberry Pi Bluetooth audio.

BlueZ owns pairing and the A2DP transport. This service talks to BlueZ over
the system D-Bus to connect an already paired phone and send AVRCP transport
commands. PipeWire or PulseAudio receives the resulting A2DP audio stream.
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from core.state import AppState

if TYPE_CHECKING:
    from dbus_next import Variant
    from dbus_next.aio import MessageBus


BLUEZ_SERVICE = "org.bluez"
OBJECT_MANAGER_PATH = "/"
DEVICE_INTERFACE = "org.bluez.Device1"
MEDIA_PLAYER_INTERFACE = "org.bluez.MediaPlayer1"
MEDIA_CONTROL_INTERFACE = "org.bluez.MediaControl1"
OBJECT_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"

ManagedProperties = Mapping[str, "Variant"]
ManagedInterfaces = Mapping[str, ManagedProperties]
ManagedObjects = Mapping[str, ManagedInterfaces]


class BluetoothServiceError(RuntimeError):
    """A recoverable error returned by BlueZ or its D-Bus transport."""


class BluetoothBackendUnavailableError(BluetoothServiceError):
    """Raised when the host cannot communicate with the BlueZ system service."""


class BluetoothPairingRequiredError(BluetoothServiceError):
    """Raised when the selected phone has not been paired and trusted yet."""


class BluetoothMediaService:
    """Read BlueZ media state and issue non-blocking AVRCP control commands."""

    def __init__(self, preferred_device_address: str = "") -> None:
        self._preferred_device_address = self._normalize_address(
            preferred_device_address
        )
        self._bus: MessageBus | None = None
        self._object_manager: Any | None = None
        self._active_device_path: str | None = None

    @staticmethod
    def is_supported_host() -> bool:
        """BlueZ's system bus is available on Linux hosts such as Raspberry Pi OS."""
        return sys.platform.startswith("linux")

    async def start(self) -> None:
        """Connect once to the system D-Bus and obtain BlueZ's object manager."""
        if self._object_manager is not None:
            return

        if not self.is_supported_host():
            raise BluetoothBackendUnavailableError(
                "BlueZ Bluetooth audio is available only on the Linux target."
            )

        try:
            from dbus_next import BusType
            from dbus_next.aio import MessageBus

            self._bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
            introspection = await self._bus.introspect(
                BLUEZ_SERVICE,
                OBJECT_MANAGER_PATH,
            )
            root_object = self._bus.get_proxy_object(
                BLUEZ_SERVICE,
                OBJECT_MANAGER_PATH,
                introspection,
            )
            self._object_manager = root_object.get_interface(OBJECT_MANAGER_INTERFACE)
        except ModuleNotFoundError as error:
            raise BluetoothBackendUnavailableError(
                "Brakuje pakietu dbus-next. Zainstaluj zależności projektu."
            ) from error
        except Exception as error:
            raise BluetoothBackendUnavailableError(
                "Nie można połączyć się z usługą BlueZ. Sprawdź usługę bluetooth."
            ) from error

    def close(self) -> None:
        """Release the D-Bus connection when the application exits."""
        if self._bus is not None:
            self._bus.disconnect()
        self._bus = None
        self._object_manager = None
        self._active_device_path = None

    async def refresh_state(self, state: AppState) -> bool:
        """Copy the latest BlueZ connection and AVRCP metadata into ``state``.

        The boolean return value allows the controller to avoid redrawing the
        dashboard when neither connectivity nor track data changed.
        """
        await self.start()
        before = self._state_snapshot(state)
        objects = await self._get_managed_objects()
        device_path, device_properties = self._select_device(objects, state)

        if device_path is None or device_properties is None:
            self._active_device_path = None
            state.bt_connected = False
            state.is_playing = False
            state.bt_connection_state = "disconnected"
            state.bt_status_message = "Nie znaleziono sparowanego telefonu"
            return before != self._state_snapshot(state)

        self._active_device_path = device_path
        state.bt_device_address = self._property_str(device_properties, "Address")
        state.bt_device_name = self._device_name(device_properties)
        state.bt_connected = self._property_bool(device_properties, "Connected")
        state.bt_connection_state = (
            "connected" if state.bt_connected else "disconnected"
        )
        state.bt_status_message = (
            f"Połączono z: {state.bt_device_name}"
            if state.bt_connected
            else f"Gotowy do połączenia: {state.bt_device_name}"
        )

        player_properties = self._find_player_properties(objects, device_path)
        if player_properties is None:
            state.is_playing = False
            return before != self._state_snapshot(state)

        self._apply_player_properties(state, player_properties)
        return before != self._state_snapshot(state)

    async def connect_saved_device(self, state: AppState) -> None:
        """Connect the configured, already paired phone through ``Device1``."""
        await self.start()
        objects = await self._get_managed_objects()
        device_path, properties = self._select_device(objects, state)
        if device_path is None or properties is None:
            raise BluetoothServiceError(
                "Nie znaleziono sparowanego urządzenia Bluetooth."
            )
        if not self._property_bool(properties, "Paired"):
            raise BluetoothPairingRequiredError(
                "Telefon nie jest sparowany. Sparuj i oznacz go jako zaufany w BlueZ."
            )

        self._active_device_path = device_path
        state.bt_connection_state = "connecting"
        state.bt_status_message = "Łączenie Bluetooth…"
        device = await self._get_interface(device_path, DEVICE_INTERFACE)
        try:
            await device.call_connect()
        except Exception as error:
            raise BluetoothServiceError("BlueZ nie mógł połączyć urządzenia.") from error

        await self.refresh_state(state)

    async def disconnect_device(self, state: AppState) -> None:
        """Disconnect all Bluetooth profiles for the selected phone."""
        await self.start()
        objects = await self._get_managed_objects()
        device_path, _ = self._select_device(objects, state)
        if device_path is None:
            return

        device = await self._get_interface(device_path, DEVICE_INTERFACE)
        try:
            await device.call_disconnect()
        except Exception as error:
            raise BluetoothServiceError("BlueZ nie mógł rozłączyć urządzenia.") from error

        await self.refresh_state(state)

    async def toggle_playback(self, state: AppState) -> None:
        """Send the appropriate AVRCP Play or Pause command to the phone."""
        await self.refresh_state(state)
        await self._send_media_command(state, "pause" if state.is_playing else "play")

    async def next_track(self, state: AppState) -> None:
        """Send the AVRCP Next command to the phone's addressed media player."""
        await self._send_media_command(state, "next")

    async def previous_track(self, state: AppState) -> None:
        """Send the AVRCP Previous command to the phone's addressed media player."""
        await self._send_media_command(state, "previous")

    async def _send_media_command(self, state: AppState, command: str) -> None:
        if not state.bt_connected:
            raise BluetoothServiceError("Telefon Bluetooth nie jest połączony.")

        objects = await self._get_managed_objects()
        device_path = self._active_device_path
        if device_path is None:
            device_path, _ = self._select_device(objects, state)
        if device_path is None:
            raise BluetoothServiceError("Nie znaleziono aktywnego urządzenia Bluetooth.")

        player_path = self._find_player_path(objects, device_path)
        interface_name = MEDIA_PLAYER_INTERFACE
        target_path = player_path
        if target_path is None:
            device_interfaces = objects.get(device_path, {})
            if MEDIA_CONTROL_INTERFACE not in device_interfaces:
                raise BluetoothServiceError(
                    "Telefon nie udostępnia sterowania AVRCP dla odtwarzacza."
                )
            target_path = device_path
            interface_name = MEDIA_CONTROL_INTERFACE

        interface = await self._get_interface(target_path, interface_name)
        method = getattr(interface, f"call_{command}", None)
        if method is None:
            raise BluetoothServiceError(
                "Podłączony odtwarzacz nie obsługuje tej komendy AVRCP."
            )
        try:
            await method()
        except Exception as error:
            raise BluetoothServiceError(
                "Telefon odrzucił komendę sterowania odtwarzaniem."
            ) from error

        # Phones update AVRCP metadata asynchronously after accepting a command.
        await asyncio.sleep(0.15)
        await self.refresh_state(state)

    async def _get_managed_objects(self) -> ManagedObjects:
        if self._object_manager is None:
            raise BluetoothBackendUnavailableError("BlueZ nie został uruchomiony.")
        return await self._object_manager.call_get_managed_objects()

    async def _get_interface(self, path: str, interface_name: str) -> Any:
        if self._bus is None:
            raise BluetoothBackendUnavailableError("Brak połączenia D-Bus.")
        introspection = await self._bus.introspect(BLUEZ_SERVICE, path)
        proxy_object = self._bus.get_proxy_object(
            BLUEZ_SERVICE,
            path,
            introspection,
        )
        return proxy_object.get_interface(interface_name)

    def _select_device(
        self,
        objects: ManagedObjects,
        state: AppState,
    ) -> tuple[str | None, ManagedProperties | None]:
        devices: list[tuple[str, ManagedProperties]] = [
            (path, interfaces[DEVICE_INTERFACE])
            for path, interfaces in objects.items()
            if DEVICE_INTERFACE in interfaces
        ]
        if not devices:
            return None, None

        preferred_address = self._preferred_device_address or self._normalize_address(
            state.bt_device_address
        )
        if preferred_address:
            for path, properties in devices:
                if self._normalize_address(
                    self._property_str(properties, "Address")
                ) == preferred_address:
                    return path, properties

        for path, properties in devices:
            if self._device_name(properties) == state.bt_device_name:
                return path, properties

        for path, properties in devices:
            if self._property_bool(properties, "Connected"):
                return path, properties

        for path, properties in devices:
            if self._property_bool(properties, "Paired"):
                return path, properties

        return None, None

    @staticmethod
    def _find_player_path(objects: ManagedObjects, device_path: str) -> str | None:
        for path, interfaces in objects.items():
            properties = interfaces.get(MEDIA_PLAYER_INTERFACE)
            if properties is None:
                continue
            if BluetoothMediaService._property_str(properties, "Device") == device_path:
                return path
        return None

    @classmethod
    def _find_player_properties(
        cls,
        objects: ManagedObjects,
        device_path: str,
    ) -> ManagedProperties | None:
        player_path = cls._find_player_path(objects, device_path)
        if player_path is None:
            return None
        return objects[player_path][MEDIA_PLAYER_INTERFACE]

    @classmethod
    def _apply_player_properties(
        cls,
        state: AppState,
        properties: ManagedProperties,
    ) -> None:
        state.is_playing = cls._property_str(properties, "Status") == "playing"
        state.track_elapsed_seconds = cls._property_float(properties, "Position") / 1000.0

        track = cls._property_mapping(properties, "Track")
        title = cls._mapping_str(track, "Title")
        artist = cls._mapping_str(track, "Artist")
        duration_ms = cls._mapping_float(track, "Duration")
        if title:
            state.current_track_title = title
        if artist:
            state.current_track_artist = artist
        if duration_ms > 0:
            state.track_duration_seconds = duration_ms / 1000.0

    @staticmethod
    def _property_bool(properties: ManagedProperties, key: str) -> bool:
        value = properties.get(key)
        return bool(value.value) if value is not None else False

    @staticmethod
    def _property_str(properties: ManagedProperties, key: str) -> str:
        value = properties.get(key)
        return str(value.value) if value is not None else ""

    @staticmethod
    def _property_float(properties: ManagedProperties, key: str) -> float:
        value = properties.get(key)
        return float(value.value) if value is not None else 0.0

    @staticmethod
    def _property_mapping(
        properties: ManagedProperties,
        key: str,
    ) -> Mapping[str, "Variant"]:
        value = properties.get(key)
        if value is None or not isinstance(value.value, Mapping):
            return {}
        return value.value

    @staticmethod
    def _mapping_str(properties: Mapping[str, "Variant"], key: str) -> str:
        value = properties.get(key)
        return str(value.value) if value is not None else ""

    @staticmethod
    def _mapping_float(properties: Mapping[str, "Variant"], key: str) -> float:
        value = properties.get(key)
        return float(value.value) if value is not None else 0.0

    @staticmethod
    def _device_name(properties: ManagedProperties) -> str:
        return (
            BluetoothMediaService._property_str(properties, "Alias")
            or BluetoothMediaService._property_str(properties, "Name")
            or "Nieznane urządzenie"
        )

    @staticmethod
    def _normalize_address(address: str) -> str:
        return address.strip().upper()

    @staticmethod
    def _state_snapshot(state: AppState) -> tuple[object, ...]:
        return (
            state.bt_connected,
            state.bt_device_name,
            state.bt_device_address,
            state.bt_connection_state,
            state.bt_status_message,
            state.is_playing,
            state.current_track_title,
            state.current_track_artist,
            state.track_elapsed_seconds,
            state.track_duration_seconds,
        )
