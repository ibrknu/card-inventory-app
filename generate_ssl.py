#!/usr/bin/env python3
"""
Generate self-signed SSL certificates for the Card Inventory App
"""

import os
import ssl
import socket
import ipaddress
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, timezone

def generate_ssl_certificates():
    """Generate self-signed SSL certificate and private key"""
    
    # Create SSL directory
    ssl_dir = Path("ssl")
    ssl_dir.mkdir(exist_ok=True)
    
    cert_file = ssl_dir / "cert.pem"
    key_file = ssl_dir / "key.pem"
    
    # Check if certificates already exist
    if cert_file.exists() and key_file.exists():
        print("✅ SSL certificates already exist!")
        return True
    
    print("🔐 Generating SSL certificates...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Get local IP address
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    
    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Card Inventory App"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now(timezone.utc)
    ).not_valid_after(
        datetime.now(timezone.utc) + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            x509.IPAddress(ipaddress.IPv4Address(local_ip)),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Write private key
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Write certificate
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print(f"✅ SSL certificates generated successfully!")
    print(f"📁 Certificate: {cert_file}")
    print(f"🔑 Private key: {key_file}")
    print(f"🌐 Valid for: localhost, 127.0.0.1, {local_ip}")
    print("⚠️  Note: This is a self-signed certificate. Browsers will show a security warning.")
    print("   Click 'Advanced' → 'Proceed' to access the app.")
    
    return True

if __name__ == "__main__":
    try:
        generate_ssl_certificates()
    except ImportError:
        print("❌ Missing required package: cryptography")
        print("Installing cryptography...")
        os.system("pip install cryptography")
        print("Please run this script again.")
    except Exception as e:
        print(f"❌ Error generating certificates: {e}")
