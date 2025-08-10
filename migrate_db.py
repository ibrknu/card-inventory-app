#!/usr/bin/env python3
"""
Database migration script to update the items table.
- Removes the condition column
- Adds price and description columns if they don't exist
Run this if you have an existing database that needs updating.
"""

import sqlite3
import os

def migrate_database():
    db_path = "./card_inventory.db"
    
    if not os.path.exists(db_path):
        print("No existing database found. The new database will be created automatically when you start the app.")
        return
    
    print(f"Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current columns
        cursor.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Remove condition column if it exists
        if 'condition' in columns:
            print("Removing condition column...")
            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            cursor.execute("""
                CREATE TABLE items_new (
                    id INTEGER PRIMARY KEY,
                    barcode VARCHAR(64),
                    name VARCHAR(255),
                    game VARCHAR(64),
                    set_name VARCHAR(128),
                    number_in_set VARCHAR(64),
                    quantity INTEGER NOT NULL DEFAULT 0,
                    location VARCHAR(128),
                    notes TEXT,
                    price DECIMAL(10,2),
                    description TEXT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """)
            
            # Copy data from old table to new table (excluding condition)
            cursor.execute("""
                INSERT INTO items_new 
                (id, barcode, name, game, set_name, number_in_set, quantity, location, notes, created_at, updated_at)
                SELECT id, barcode, name, game, set_name, number_in_set, quantity, location, notes, created_at, updated_at
                FROM items
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE items")
            cursor.execute("ALTER TABLE items_new RENAME TO items")
            
            # Recreate indexes
            cursor.execute("CREATE INDEX ix_items_barcode ON items(barcode)")
            cursor.execute("CREATE INDEX ix_items_id ON items(id)")
            cursor.execute("CREATE UNIQUE INDEX uq_items_barcode ON items(barcode)")
        
        # Add price column if it doesn't exist
        cursor.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'price' not in columns:
            print("Adding price column...")
            cursor.execute("ALTER TABLE items ADD COLUMN price DECIMAL(10,2)")
        
        if 'description' not in columns:
            print("Adding description column...")
            cursor.execute("ALTER TABLE items ADD COLUMN description TEXT")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 