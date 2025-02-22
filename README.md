# WiFi & GPS Scanner

## Overview
This script scans for Wi-Fi networks and associates each scan result with GPS coordinates. It is useful for mapping Wi-Fi network locations or conducting research on network availability in different areas.

## Features
- Detects available Wi-Fi interfaces.
- Scans Wi-Fi networks and retrieves SSID and signal strength.
- Detects connected GPS devices.
- Extracts GPS coordinates (latitude and longitude) from the selected GPS device.
- Associates Wi-Fi scan results with corresponding GPS locations.
- Saves the scan results to a timestamped file.

## Requirements
### Software Dependencies
Ensure the following dependencies are installed before running the script:
- Python 3.x
- `pynmea2` (for parsing GPS data)
- `pyserial` (for reading GPS device data)
- `iwconfig` (for detecting Wi-Fi interfaces)
- `iwlist` (for scanning Wi-Fi networks)

### Installation
Use the following commands to install the required dependencies:
```sh
pip install pynmea2 pyserial
```
For `iwconfig` and `iwlist`, install them using:
```sh
sudo apt install wireless-tools
```

## Usage
1. **Run the script:**
   ```sh
   python wifi_gps_scanner.py
   ```
2. **Select a Wi-Fi interface** from the available list.
3. **Select a GPS device** (if detected) or continue without GPS.
4. The script will scan Wi-Fi networks and log their SSID, signal strength, and GPS location (if available) every 60 seconds.
5. **Stop the scan** using `Ctrl+C`.
6. Scan results are saved in a timestamped `.txt` file in the same directory.

## File Output Format
The scan results are saved in the following format:
```
Wi-Fi & GPS Scan Results at YYYY-MM-DD_HH-MM-SS

SSID: Seen <count> times, Max Signal Strength: <dBm>, Location: (Latitude, Longitude)
```

## Notes
- If no GPS device is found, Wi-Fi scans will proceed without location data.
- GPS coordinates are only logged if valid data is received from the GPS device.
- The script requires **root privileges** to perform Wi-Fi scanning (`sudo` may be needed).

## License
This script is open-source and provided under the MIT License. Modify and use it as needed!

