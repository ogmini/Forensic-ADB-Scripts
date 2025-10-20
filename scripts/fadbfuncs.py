"""
File: fadbfuncs.py
Description: TODO
Author: ogmini (https://ogmini.github.io/)
Created: 2025-10-19
Modified: 2025-10-19
Version: 0.1
License: MIT
Usage:
    Library of utilities used by other scripts

Dependencies:
    - ADB (Android Debug Bridge) - https://developer.android.com/tools/adb
    - Python 3.6+
"""

import subprocess
import argparse
import re
import ipaddress

def run_adb_command(cmd, track_progress=False):
    if not track_progress:        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error {' '.join(cmd)}:\n{result.stderr}")
            return []
        return result.stdout.strip().splitlines()
    
#TODO: This is not working as hoped.    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout_lines = []
    while True:
        # Read from stdout if needed
        out_line = process.stdout.readline()
        if out_line:
            print(out_line)
            stdout_lines.append(out_line.strip())

        # Read from stderr for progress
        err_line = process.stderr.readline()
        if err_line:
            # Example: print progress info or parse it
            print(err_line.strip())

        # Check if process ended
        if out_line == '' and err_line == '' and process.poll() is not None:
            break

    if process.returncode != 0:
        print(f"Error {' '.join(cmd)}: exited with code {process.returncode}")
        return None

    return stdout_lines
       
def is_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True  # It is an IP
    except ValueError:
        return False   # Not an IP
    
def is_ip_with_port(ip):
    if ':' not in ip:
        return False
    ip_part, port_part = ip.rsplit(':', 1)
    
    try:
        ipaddress.ip_address(ip_part)
    except ValueError:
        return False
    
    if not port_part.isdigit():
        return False
    port = int(port_part)
    return 0 < port <= 65535

    
def adb_connect_wifi():
    device_ip = "0.0.0.0"
    
    input("Connect Device via USB and press enter to continue...")
    
    # Verify USB
    devices_command = ["adb", "devices"]
    devices = run_adb_command(devices_command)
    print(devices[1].split()[0])
    if is_ip(devices[1].split()[0]):
        print("Error")
        #TODO: Exit with error
    
    # Get IP of Phone via adb shell. This seems precarious....
    ip_command = ["adb", "shell", "ip -f inet add show wlan0"]
    ip_result = run_adb_command(ip_command)
    # print(ip_result[1])
    
    match = re.search(r'\binet (\d+\.\d+\.\d+\.\d+)', ip_result[1])
    if match:
        device_ip = match.group(1)
        print("IP Address:", device_ip)
    else:
        print("No IP address found.")
    
    # Restart Daemon in TCPIP mode
    tcpip_command = ["adb", "tcpip", "5555"]
    tcpip = run_adb_command(tcpip_command)
    print(tcpip[0])
    
    input("Disconnect USB cable and press enter to continue...")
    
    # Connect via TCP/IP adb connect 192.168.0.218
    tcpip_command = ["adb", "connect", device_ip]
    tcpip = run_adb_command(tcpip_command)
    print(tcpip[0])
    
def adb_disconnect_wifi():
    # TODO: Get IP for adb devices
    device_ip = "0.0.0.0"
    
    # Verify USB
    devices_command = ["adb", "devices"]
    devices = run_adb_command(devices_command)
    device_ip = devices[1].split()[0]
    print(device_ip)
    if is_ip_with_port(device_ip):
        # Disconnect TCP/IP adb disconnect 192.168.0.218:5555
        tcpip_command = ["adb", "disconnect", device_ip]
        tcpip = run_adb_command(tcpip_command)
        print(tcpip)
    else:
        print("ERROR ON DISCONNECT")
        #TODO: Exit with error
        
    #TODO: Do we NEED to reconnect with USB and issue adb usb?
    input("Reconnect USB cable and press enter to continue...")
    
    usb_command = ["adb", "usb"]
    usb = run_adb_command(usb_command)
    print(usb)
    
    