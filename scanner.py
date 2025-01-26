import os
import subprocess
import time
from datetime import datetime

def get_wifi_interfaces():
    # Get a list of available wifi interfaces
    interfaces = []
    try:
        result = subprocess.check_output(['iwconfig'], stderr=subprocess.STDOUT, universal_newlines=True)
        for line in result.splitlines():
            if "IEEE 802.11" in line:
                interface_name = line.split()[0]
                interfaces.append(interface_name)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching wifi interfaces: {e}")
    return interfaces

def scan_networks(interface):
    # Scan for Wi-Fi networks using iwlist
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
                    # Handle the case where the signal level is in the format 'XX/YY'
                    signal_strength_str = line.split("=")[1].split(" ")[0]
                    signal_strength = int(signal_strength_str.split("/")[0])  # Get the first part before '/'
                
                if ssid and signal_strength:
                    networks.append((ssid, signal_strength))
                    break  # Move on to the next network
    except subprocess.CalledProcessError as e:
        print(f"Error scanning networks: {e}")
    
    return networks

def update_network_data(networks, network_data):
    # Update the network data dictionary
    for ssid, signal_strength in networks:
        if ssid in network_data:
            count, max_strength = network_data[ssid]
            network_data[ssid] = (count + 1, max(signal_strength, max_strength))
        else:
            network_data[ssid] = (1, signal_strength)

def save_to_file(network_data):
    # Save network data to a file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"wifi_scan_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Wifi Scan Results at {timestamp}\n\n")
        for ssid, (count, max_strength) in network_data.items():
            f.write(f"{ssid}: Seen {count} times, Max Signal Strength: {max_strength} dBm\n")
    
    print(f"Results saved to {filename}")

def main():
    # Get available interfaces and prompt the user to select one
    interfaces = get_wifi_interfaces()
    if len(interfaces) == 0:
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
    
    # Initialize the network data dictionary
    network_data = {}
    
    try:
        while True:
            print("\nScanning for networks...")
            networks = scan_networks(interface)
            update_network_data(networks, network_data)
            
            # Save the current scan data to a file every 10 minutes
            save_to_file(network_data)
            
            # Wait for 60 seconds before the next scan
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nScan stopped by user.")

if __name__ == "__main__":
    main()
