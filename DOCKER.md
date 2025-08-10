# Docker usage for Card Inventory

## Prerequisites
- Docker and Docker Compose installed
- Project directory: `/home/ibrknu/.config/sublime-text/Packages/User/card_inventory`

## Development (HTTP)

```bash
cd /home/ibrknu/.config/sublime-text/Packages/User/card_inventory
docker compose build
docker compose up -d
```

Open in browser (iPhone or desktop):
- `http://YOUR_COMPUTER_LAN_IP:8000/`
- API docs: `http://YOUR_COMPUTER_LAN_IP:8000/docs`

## Production (HTTPS with SSL)

### Prerequisites for SSL
- A domain name pointing to your server
- Ports 80 and 443 open on your server
- Email address for Let's Encrypt notifications

### Setup SSL

1. **Configure your domain**:
```bash
cd /home/ibrknu/.config/sublime-text/Packages/User/card_inventory
./ssl-setup.sh your-domain.com your-email@example.com
```

2. **Start production stack**:
```bash
docker compose -f docker-compose.prod.yml up -d
```

3. **Access your app**:
- `https://your-domain.com/`
- API docs: `https://your-domain.com/docs`

### SSL Certificate Renewal

Add to crontab for automatic renewal:
```bash
crontab -e
# Add this line:
0 12 * * * cd /home/ibrknu/.config/sublime-text/Packages/User/card_inventory && docker compose -f docker-compose.prod.yml run --rm certbot renew && docker compose -f docker-compose.prod.yml restart nginx
```

## Data persistence
- Database stored in a named volume: `card_inventory_data` at `/data/card_inventory.db` inside the container.
- SSL certificates stored in `certbot-etc` and `certbot-var` volumes.

To inspect the DB file locally:
```bash
docker compose run --rm api ls -al /data
```

## Logs and lifecycle
```bash
# Development
docker compose logs -f
docker compose restart
docker compose down

# Production
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml restart
docker compose -f docker-compose.prod.yml down
```

## Environment variables
- `CARD_INV_DB_URL` (default `sqlite:////data/card_inventory.db`)

To use a different DB path (still SQLite):
```yaml
environment:
  - CARD_INV_DB_URL=sqlite:////data/my_cards.db
```

## Without Compose
```bash
# Build
docker build -t card-inventory:latest /home/ibrknu/.config/sublime-text/Packages/User/card_inventory

# Run
docker run -d --name card_inventory_api \
  -p 8000:8000 \
  -e CARD_INV_DB_URL=sqlite:////data/card_inventory.db \
  -v card_inventory_data:/data \
  -v /home/ibrknu/.config/sublime-text/Packages/User/card_inventory:/app \
  card-inventory:latest
```

## Troubleshooting

### iPhone camera access issues
- Use HTTPS (production setup) instead of HTTP
- Ensure camera permissions are granted in Safari
- Try adding the site to Home Screen for better permissions

### SSL certificate issues
- Check domain DNS is pointing to your server
- Ensure ports 80 and 443 are open
- Verify Let's Encrypt rate limits (max 5 certs per domain per week)

### Database issues
- Check volume permissions: `docker volume ls`
- Backup: `docker run --rm -v card_inventory_data:/data -v $(pwd):/backup alpine tar czf /backup/db-backup.tar.gz /data/`