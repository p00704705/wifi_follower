import os
import subprocess
import time
import serial
import pynmea2
from datetime import datetime

def get_wifi_interfaces():
    interfaces = []
    try:
        result = subprocess.check_output(['iwconfig'], stderr=subprocess.STDOUT, universal_newlines=True)
        for line in result.splitlines():
            if "IEEE 802.11" in line:
                interface_name = line.split()[0]
                interfaces.append(interface_name)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching Wi-Fi interfaces: {e}")
    return interfaces

def scan_networks(interface):
    networks = []
    try:
        result = subprocess.check_output(['sudo', 'iwlist', interface, 'scan'], stderr=subprocess.STDOUT, universal_newlines=True)
        networks_data = result.split("Cell ")
        
        for network in networks_data[1:]:
            ssid = None
            signal_strength = None
            
            for line in network.splitlines():
                if "ESSID" in line:
                    ssid = line.split(":")[1].strip('"')
                elif "Signal level" in line:
                    signal_strength_str = line.split("=")[1].split(" ")[0]
                    signal_strength = int(signal_strength_str.split("/")[0])  
                
                if ssid and signal_strength:
                    networks.append((ssid, signal_strength))
                    break  
    except subprocess.CalledProcessError as e:
        print(f"Error scanning networks: {e}")
    
    return networks

def scan_gps_devices():
    possible_ports = [
        '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyAMA0', '/dev/ttyAMA1', '/dev/ttyACM0'
    ]
    available_ports = []
    
    for port in possible_ports:
        try:
            with serial.Serial(port, 9600, timeout=1) as ser:
                available_ports.append(port)
        except serial.SerialException:
            continue
    
    return available_ports

def get_gps_coordinates(port):
    try:
        with serial.Serial(port, 9600, timeout=1) as ser:
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith('$GNGGA') or line.startswith('$GNRMC'):
                    try:
                        msg = pynmea2.parse(line)
                        latitude, longitude = msg.latitude, msg.longitude
                        if latitude and longitude:
                            return latitude, longitude
                    except pynmea2.ParseError:
                        continue
    except serial.SerialException as e:
        print(f"Error reading GPS data: {e}")
    return None, None

def save_to_file(network_data):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"wifi_gps_scan_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Wi-Fi & GPS Scan Results at {timestamp}\n\n")
        for ssid, (count, max_strength, latitude, longitude) in network_data.items():
            f.write(f"{ssid}: Seen {count} times, Max Signal Strength: {max_strength} dBm, Location: ({latitude}, {longitude})\n")
    
    print(f"Results saved to {filename}")

def main():
    interfaces = get_wifi_interfaces()
    if not interfaces:
        print("No Wi-Fi interfaces found.")
        return
    
    print("Available Wi-Fi interfaces:")
    for idx, interface in enumerate(interfaces):
        print(f"{idx + 1}. {interface}")
    
    interface_choice = int(input("Choose a Wi-Fi interface by number: ")) - 1
    if interface_choice < 0 or interface_choice >= len(interfaces):
        print("Invalid choice. Exiting.")
        return
    
    interface = interfaces[interface_choice]
    print(f"Using interface: {interface}")
    
    gps_devices = scan_gps_devices()
    if not gps_devices:
        print("No GPS devices found. Proceeding without location data.")
        gps_port = None
    else:
        print("Available GPS devices:")
        for idx, port in enumerate(gps_devices):
            print(f"{idx + 1}. {port}")
        
        gps_choice = int(input("Choose a GPS device by number: ")) - 1
        if gps_choice < 0 or gps_choice >= len(gps_devices):
            print("Invalid choice. Exiting.")
            return
        
        gps_port = gps_devices[gps_choice]
    
    network_data = {}
    try:
        while True:
            print("\nScanning for networks...")
            networks = scan_networks(interface)
            latitude, longitude = get_gps_coordinates(gps_port) if gps_port else (None, None)
            
            for ssid, signal_strength in networks:
                if ssid in network_data:
                    count, max_strength, lat, lon = network_data[ssid]
                    network_data[ssid] = (count + 1, max(signal_strength, max_strength), latitude, longitude)
                else:
                    network_data[ssid] = (1, signal_strength, latitude, longitude)
            
            save_to_file(network_data)
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nScan stopped by user.")

if __name__ == "__main__":
    main()
