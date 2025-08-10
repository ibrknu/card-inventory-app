#!/usr/bin/env python3
"""
Get current IP address for network access
"""

import socket
import subprocess

def get_local_ip():
    try:
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return None

def get_network_ip():
    try:
        # Try to get IP from ip command
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'inet ' in line and 'global' in line:
                ip = line.split()[1].split('/')[0]
                if not ip.startswith('127.'):
                    return ip
    except:
        pass
    return None

if __name__ == "__main__":
    local_ip = get_local_ip()
    network_ip = get_network_ip()
    
    print("🌐 Network Information:")
    print(f"Local IP: {local_ip}")
    print(f"Network IP: {network_ip}")
    print()
    print("📱 Access from iPhone:")
    if network_ip:
        print(f"HTTPS: https://{network_ip}:8443")
        print(f"HTTP:  http://{network_ip}:8000")
    else:
        print(f"HTTPS: https://{local_ip}:8443")
        print(f"HTTP:  http://{local_ip}:8000")
    print()
    print("💻 Access from computer:")
    print(f"HTTPS: https://localhost:8443")
    print(f"HTTP:  http://localhost:8000") 