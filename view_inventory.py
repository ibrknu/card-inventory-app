#!/usr/bin/env python3
"""
View Card Inventory
This script displays all items in your card inventory database.
"""

import sqlite3
from pathlib import Path
from tabulate import tabulate

def view_inventory():
    """Display all items in the inventory"""
    
    db_path = Path("card_inventory.db")
    
    if not db_path.exists():
        print("❌ Database not found! Please run the app first to create the database.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all items
        cursor.execute("""
            SELECT id, name, game, set_name, number_in_set, quantity, location, price, created_at
            FROM items 
            ORDER BY created_at DESC
        """)
        
        items = cursor.fetchall()
        
        if not items:
            print("📭 No items found in inventory.")
            print("Start the app and scan some cards to add them!")
            return
        
        print(f"📊 Card Inventory - {len(items)} items found")
        print("=" * 80)
        
        # Prepare data for tabulate
        headers = ["ID", "Name", "Game", "Set", "#", "Qty", "Location", "Price", "Added"]
        table_data = []
        
        for item in items:
            id, name, game, set_name, number, qty, location, price, created = item
            table_data.append([
                id,
                name or "Unknown",
                game or "Unknown",
                set_name or "Unknown",
                number or "N/A",
                qty,
                location or "Unknown",
                f"${price:.2f}" if price else "N/A",
                created[:10] if created else "Unknown"
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Summary statistics
        cursor.execute("SELECT COUNT(*), SUM(quantity), SUM(price * quantity) FROM items")
        total_items, total_quantity, total_value = cursor.fetchone()
        
        print(f"\n📈 Summary:")
        print(f"   Total unique cards: {total_items}")
        print(f"   Total quantity: {total_quantity or 0}")
        print(f"   Estimated value: ${total_value:.2f}" if total_value else "   Estimated value: N/A")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

def search_inventory(search_term):
    """Search for specific items"""
    
    db_path = Path("card_inventory.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Search items
        cursor.execute("""
            SELECT id, name, game, set_name, number_in_set, quantity, location, price
            FROM items 
            WHERE name LIKE ? OR game LIKE ? OR set_name LIKE ? OR barcode LIKE ?
            ORDER BY name
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        
        items = cursor.fetchall()
        
        if not items:
            print(f"🔍 No items found matching '{search_term}'")
            return
        
        print(f"🔍 Search results for '{search_term}' - {len(items)} items found")
        print("=" * 80)
        
        headers = ["ID", "Name", "Game", "Set", "#", "Qty", "Location", "Price"]
        table_data = []
        
        for item in items:
            id, name, game, set_name, number, qty, location, price = item
            table_data.append([
                id,
                name or "Unknown",
                game or "Unknown",
                set_name or "Unknown",
                number or "N/A",
                qty,
                location or "Unknown",
                f"${price:.2f}" if price else "N/A"
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error searching database: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
        search_inventory(search_term)
    else:
        view_inventory()
