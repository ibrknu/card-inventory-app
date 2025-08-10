#!/usr/bin/env python3
"""
HTTPS Server for Card Inventory App
This script runs the FastAPI app with SSL certificates for secure camera access.
"""

import uvicorn
import ssl
from pathlib import Path
from get_ip import get_local_ip, get_network_ip

if __name__ == "__main__":
    # SSL certificate paths
    ssl_dir = Path("ssl")
    cert_file = ssl_dir / "cert.pem"
    key_file = ssl_dir / "key.pem"
    
    # Check if SSL files exist
    if not cert_file.exists() or not key_file.exists():
        print("❌ SSL certificates not found!")
        print("Please run: mkdir -p ssl && cd ssl && openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/C=US/ST=State/L=City/O=Organization/CN=localhost'")
        exit(1)
    
    # Get current IP addresses
    local_ip = get_local_ip()
    network_ip = get_network_ip()
    
    print("🔒 Starting HTTPS server...")
    print("📱 Access from iPhone:")
    if network_ip:
        print(f"HTTPS: https://{network_ip}:8443")
        print(f"HTTP:  http://{network_ip}:8000")
    else:
        print(f"HTTPS: https://{local_ip}:8443")
        print(f"HTTP:  http://{local_ip}:8000")
    print("💻 Access from computer: https://localhost:8443")
    print("⚠️  Note: You'll see a security warning - click 'Advanced' → 'Proceed'")
    print("Press Ctrl+C to stop")
    
    # Run with HTTPS
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8443,
        reload=True,
        ssl_keyfile=str(key_file),
        ssl_certfile=str(cert_file),
        log_level="info"
    ) 