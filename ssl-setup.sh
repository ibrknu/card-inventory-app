#!/bin/bash

# SSL Setup Script for Card Inventory
# Usage: ./ssl-setup.sh your-domain.com your-email@example.com

set -e

DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"your-email@example.com"}

if [ "$DOMAIN" = "your-domain.com" ] || [ "$EMAIL" = "your-email@example.com" ]; then
    echo "Usage: $0 <domain> <email>"
    echo "Example: $0 cards.example.com user@example.com"
    exit 1
fi

echo "Setting up SSL for domain: $DOMAIN"
echo "Email: $EMAIL"

# Create required directories
mkdir -p ssl
mkdir -p certbot-etc
mkdir -p certbot-var

# Update nginx.conf with domain
sed -i "s/your-domain.com/$DOMAIN/g" nginx.conf

# Update docker-compose.prod.yml with domain and email
sed -i "s/your-domain.com/$DOMAIN/g" docker-compose.prod.yml
sed -i "s/your-email@example.com/$EMAIL/g" docker-compose.prod.yml

# Create initial nginx container for certbot challenge
echo "Starting nginx for certificate challenge..."
docker compose -f docker-compose.prod.yml up nginx -d

# Wait for nginx to start
sleep 5

# Get initial certificate
echo "Requesting SSL certificate from Let's Encrypt..."
docker compose -f docker-compose.prod.yml run --rm certbot

# Restart nginx with SSL
echo "Restarting nginx with SSL..."
docker compose -f docker-compose.prod.yml restart nginx

echo "SSL setup complete!"
echo "Access your app at: https://$DOMAIN"
echo ""
echo "To renew certificates (add to crontab):"
echo "0 12 * * * cd $(pwd) && docker compose -f docker-compose.prod.yml run --rm certbot renew && docker compose -f docker-compose.prod.yml restart nginx" 