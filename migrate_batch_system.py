#!/usr/bin/env python3
"""
Migration script to add batch system to existing database.
This script will:
1. Create the batches table
2. Add batch_id column to items table
3. Update existing items to have valid location values
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    # Get the database path
    db_path = Path(__file__).parent / "card_inventory.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    print(f"Migrating database at {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if batches table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batches'")
        if cursor.fetchone():
            print("Batches table already exists, skipping creation")
        else:
            # Create batches table
            print("Creating batches table...")
            cursor.execute("""
                CREATE TABLE batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    target_location VARCHAR(64) NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
                    updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
                )
            """)
            print("✓ Batches table created")
        
        # Check if batch_id column exists in items table
        cursor.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'batch_id' not in columns:
            # Add batch_id column to items table
            print("Adding batch_id column to items table...")
            cursor.execute("ALTER TABLE items ADD COLUMN batch_id INTEGER REFERENCES batches(id)")
            print("✓ batch_id column added")
        else:
            print("batch_id column already exists")
        
        # Update existing items to have valid location values
        print("Updating existing items with valid location values...")
        cursor.execute("""
            UPDATE items 
            SET location = 'Storage' 
            WHERE location IS NULL OR location = '' OR location NOT IN ('Storage', 'Show')
        """)
        updated_count = cursor.fetchone()[0] if cursor.fetchone() else 0
        print(f"✓ Updated {updated_count} items with default location")
        
        # Commit changes
        conn.commit()
        print("✓ Migration completed successfully")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
