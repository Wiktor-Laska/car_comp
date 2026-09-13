# Bluetooth Audio on Raspberry Pi 4

The application uses BlueZ over the system D-Bus to connect a phone and send
AVRCP transport commands. PipeWire (or PulseAudio) receives the phone's A2DP
audio stream and routes it to the Pi's configured audio output.

## One-time Pi setup

On Raspberry Pi OS, install and enable the Bluetooth and audio services:

```bash
sudo apt update
sudo apt install -y bluez pipewire pipewire-pulse wireplumber
python -m pip install -r requirements.txt
sudo systemctl enable --now bluetooth
systemctl --user enable --now pipewire pipewire-pulse wireplumber
```

Pair and trust the phone once from the Pi terminal. Replace the address with
the phone discovered by `scan on`:

```text
bluetoothctl
power on
agent on
default-agent
scan on
pair AA:BB:CC:DD:EE:FF
trust AA:BB:CC:DD:EE:FF
quit
```

Start the infotainment app with the paired phone's address. This prevents the
head unit from connecting to an unintended paired device:

```bash
export MAZDA_BT_DEVICE_ADDRESS=AA:BB:CC:DD:EE:FF
python main.py
```

The Bluetooth screen's **POŁĄCZ** button invokes BlueZ `Device1.Connect`.
Play/pause and track buttons invoke the connected phone's AVRCP media player.
If a phone does not expose AVRCP metadata, the connection and audio stream can
still work, but title, artist, and transport controls depend on the phone and
its music application.
