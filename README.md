# Card Inventory (Trading Cards)

FastAPI + SQLite backend with a lightweight web UI for scanning barcodes using an iPhone. Designed to quickly record what you have on hand and update quantities by scanning.

## Quickstart

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the server:

```bash
uvicorn card_inventory.app.main:app --reload --host 0.0.0.0 --port 8000
```

3. On your iPhone, open Safari and visit:

- `http://YOUR_COMPUTER_LAN_IP:8000/`
- Grant camera permissions when prompted. Scan barcodes and they will be posted to the backend.

4. API docs:

- Swagger UI: `http://YOUR_COMPUTER_LAN_IP:8000/docs`

## Features

- Web-based scanner that uses your iPhone camera (no install required)
- Add or increment items by scanning barcodes
- **New**: Automatic form for unrecognized barcodes to add price and description
- REST API for items and scan events
- SQLite database for local, simple storage

## iPhone Input Options (Suggestions)

- Web app (recommended): Use the built-in scanner at `/` in Safari. You can add it to Home Screen as a PWA-like shortcut.
- Shortcuts app: Create a Shortcut that scans a code and makes an HTTP POST to `http://YOUR_IP:8000/api/scan` with JSON `{ "barcode": "..." }`.
- Third-party scanner apps: Many can be configured to open a URL with the code appended, e.g., `http://YOUR_IP:8000/api/scan?barcode=...` (use GET for quick tests; POST is preferred).
- Dedicated iOS app (future): A native Swift app using AVFoundation for scanning that POSTs to the same API.

## Data Model (baseline)

- Item: `id`, `barcode?`, `name?`, `game?`, `set_name?`, `number_in_set?`, `quantity`, `location?`, `notes?`, `price?`, `description?`, timestamps
- ScanEvent: `id`, `barcode`, `created_at`

Note: Many trading cards do not have unique barcodes per card. If you need per-card tracking, consider printing your own QR labels and scanning those. The included UI can also accept manual entry if scanning isn’t available.

## Configuration

- Database: Defaults to `sqlite:///./card_inventory.db` in the project root.
- CORS: Open for local network by default.

## Common Tasks

- Reset database (dangerous): delete `card_inventory.db`.
- Export items: use `/api/items` to fetch JSON, or build a small export script.
- **Database migration**: If you have an existing database, run `python migrate_db.py` to update the schema.

## New Features

### Unrecognized Barcode Handling
When you scan a barcode that's not in the database:
1. The app automatically creates a basic item entry
2. A modal form appears to add details like name, price, description, etc.
3. You can specify game type, condition, location, and other metadata
4. The item is saved with all the details you provide

This makes it easy to quickly catalog new items as you scan them!

## Next Steps / Clarifications

If you want this fine-tuned, please specify:
- Which games (e.g., Pokémon, MTG, Yu-Gi-Oh!, Sports)?
- Do your items have scannable barcodes, or should we generate/print QR labels?
- Fields you want to track (condition scale, acquisition cost, graded status, binder/box location, etc.).
- Single-user local vs. multi-user sync.