#!/bin/bash
# Start HTTPS Server for Card Inventory App

echo "🔒 Starting Card Inventory HTTPS Server..."
echo ""

# Activate virtual environment
source .venv/bin/activate

# Get current IP
echo "🌐 Network Information:"
python get_ip.py
echo ""

# Start HTTPS server
echo "🚀 Starting server..."
python run_https.py 