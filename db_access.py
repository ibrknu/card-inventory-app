#!/usr/bin/env python3
"""
Database Access Script for Card Inventory
Use this script to query and manage your card inventory database.
"""

import sqlite3
from datetime import datetime
import sys

def connect_db():
    """Connect to the SQLite database"""
    try:
        conn = sqlite3.connect('card_inventory.db')
        conn.row_factory = sqlite3.Row  # This allows column access by name
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def show_all_items():
    """Display all items in the database"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, barcode, name, game, set_name, number_in_set, 
               quantity, location, price, created_at 
        FROM items 
        ORDER BY created_at DESC
    """)
    
    items = cursor.fetchall()
    
    if not items:
        print("No items found in database.")
        return
    
    print(f"\n{'ID':<3} {'Barcode':<15} {'Name':<20} {'Game':<15} {'Set':<15} {'#':<5} {'Qty':<4} {'Location':<12} {'Price':<8}")
    print("-" * 120)
    
    for item in items:
        print(f"{item['id']:<3} {item['barcode']:<15} {item['name']:<20} {item['game']:<15} {item['set_name']:<15} {item['number_in_set']:<5} {item['quantity']:<4} {item['location']:<12} {item['price']:<8}")
    
    conn.close()

def search_by_barcode(barcode):
    """Search for an item by barcode"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE barcode = ?", (barcode,))
    item = cursor.fetchone()
    
    if item:
        print(f"\nItem found:")
        print(f"  ID: {item['id']}")
        print(f"  Barcode: {item['barcode']}")
        print(f"  Name: {item['name']}")
        print(f"  Game: {item['game']}")
        print(f"  Set: {item['set_name']}")
        print(f"  Number: {item['number_in_set']}")
        print(f"  Quantity: {item['quantity']}")
        print(f"  Location: {item['location']}")
        print(f"  Price: {item['price']}")
        print(f"  Notes: {item['notes']}")
        print(f"  Description: {item['description']}")
        print(f"  Created: {item['created_at']}")
        print(f"  Updated: {item['updated_at']}")
    else:
        print(f"No item found with barcode: {barcode}")
    
    conn.close()

def search_by_name(name):
    """Search for items by name (partial match)"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE name LIKE ? ORDER BY name", (f"%{name}%",))
    items = cursor.fetchall()
    
    if items:
        print(f"\nFound {len(items)} item(s) matching '{name}':")
        for item in items:
            print(f"  {item['id']}: {item['name']} ({item['barcode']}) - Qty: {item['quantity']}")
    else:
        print(f"No items found matching: {name}")
    
    conn.close()

def show_statistics():
    """Show database statistics"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Total items
    cursor.execute("SELECT COUNT(*) FROM items")
    total_items = cursor.fetchone()[0]
    
    # Items with names
    cursor.execute("SELECT COUNT(*) FROM items WHERE name IS NOT NULL AND name != ''")
    named_items = cursor.fetchone()[0]
    
    # Total quantity
    cursor.execute("SELECT SUM(quantity) FROM items")
    total_quantity = cursor.fetchone()[0] or 0
    
    # Total value
    cursor.execute("SELECT SUM(quantity * COALESCE(price, 0)) FROM items")
    total_value = cursor.fetchone()[0] or 0
    
    # Recent scans
    cursor.execute("SELECT COUNT(*) FROM scan_events WHERE created_at > datetime('now', '-7 days')")
    recent_scans = cursor.fetchone()[0]
    
    print(f"\nDatabase Statistics:")
    print(f"  Total items: {total_items}")
    print(f"  Items with names: {named_items}")
    print(f"  Total quantity: {total_quantity}")
    print(f"  Estimated total value: ${total_value:.2f}")
    print(f"  Scans in last 7 days: {recent_scans}")
    
    conn.close()

def show_recent_scans(limit=10):
    """Show recent scan events"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.created_at, s.barcode, i.name 
        FROM scan_events s 
        LEFT JOIN items i ON s.barcode = i.barcode 
        ORDER BY s.created_at DESC 
        LIMIT ?
    """, (limit,))
    
    scans = cursor.fetchall()
    
    if scans:
        print(f"\nRecent {len(scans)} scans:")
        print(f"{'Date':<20} {'Barcode':<15} {'Name':<30}")
        print("-" * 65)
        for scan in scans:
            name = scan['name'] if scan['name'] else 'Unknown'
            print(f"{scan['created_at']:<20} {scan['barcode']:<15} {name:<30}")
    else:
        print("No scan events found.")
    
    conn.close()

def main():
    """Main function with menu"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "all":
            show_all_items()
        elif command == "stats":
            show_statistics()
        elif command == "scans":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            show_recent_scans(limit)
        elif command == "search" and len(sys.argv) > 2:
            search_by_name(sys.argv[2])
        elif command == "barcode" and len(sys.argv) > 2:
            search_by_barcode(sys.argv[2])
        else:
            print("Usage:")
            print("  python db_access.py all                    # Show all items")
            print("  python db_access.py stats                  # Show statistics")
            print("  python db_access.py scans [limit]          # Show recent scans")
            print("  python db_access.py search <name>          # Search by name")
            print("  python db_access.py barcode <barcode>      # Search by barcode")
    else:
        # Interactive menu
        while True:
            print("\n" + "="*50)
            print("CARD INVENTORY DATABASE ACCESS")
            print("="*50)
            print("1. Show all items")
            print("2. Show statistics")
            print("3. Show recent scans")
            print("4. Search by barcode")
            print("5. Search by name")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                show_all_items()
            elif choice == "2":
                show_statistics()
            elif choice == "3":
                limit = input("Number of scans to show (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                show_recent_scans(limit)
            elif choice == "4":
                barcode = input("Enter barcode: ").strip()
                if barcode:
                    search_by_barcode(barcode)
            elif choice == "5":
                name = input("Enter name to search: ").strip()
                if name:
                    search_by_name(name)
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
