# Batch Management System

## Overview

The batch management system allows users to create temporary collections of items that can be transferred to a specific location (Storage or Show) as a group. This is particularly useful for organizing items for events, shows, or bulk transfers.

## Key Features

### 🎯 **Active Batch Scanning**
- When an active batch is selected, all scanned items are automatically added to that batch
- Items in a batch are automatically assigned the batch's target location
- Visual indicator shows which batch is currently active

### 📦 **Batch Creation**
- Create batches with custom names and descriptions
- Specify target location (Storage or Show) for all items in the batch
- Batches can be active or inactive

### 🔄 **Batch Transfer**
- Transfer all items in a batch to their target location at once
- Automatically removes items from the batch after transfer
- Deactivates the batch after successful transfer

### ❌ **Batch Cancellation**
- Cancel a batch to remove all items from it
- Items return to their previous state (no batch association)
- Useful for correcting mistakes or changing plans

## Database Changes

### New Table: `batches`
```sql
CREATE TABLE batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    target_location VARCHAR(64) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
);
```

### Updated Table: `items`
- Added `batch_id` column (foreign key to batches.id)
- Updated `location` field to only accept "Storage" or "Show" values
- Added validation to ensure location values are valid

## API Endpoints

### Batch Management
- `POST /api/batches/` - Create a new batch
- `GET /api/batches/` - List all batches (with optional active_only filter)
- `GET /api/batches/{batch_id}` - Get batch details with items
- `PUT /api/batches/{batch_id}` - Update batch
- `DELETE /api/batches/{batch_id}` - Delete batch

### Batch Operations
- `POST /api/batches/{batch_id}/scan` - Add item to batch by scanning
- `POST /api/batches/{batch_id}/transfer` - Transfer or cancel batch

## User Workflow

### Creating and Using a Batch

1. **Create Batch**
   - Click "Create New Batch"
   - Enter batch name and description
   - Select target location (Storage or Show)
   - Click "Create Batch"

2. **Activate Batch**
   - The newly created batch becomes active automatically
   - Active batch is shown in the interface

3. **Scan Items to Batch**
   - With active batch, scan items normally
   - Items are automatically added to the batch
   - Items get the batch's target location

4. **Transfer Batch**
   - View batch details to see all items
   - Click "Transfer Batch" to move all items to target location
   - Batch is deactivated after transfer

### Batch Management

- **View All Batches**: Click "View Batches" to see all batches
- **View Batch Details**: Click "View" on any batch to see its items
- **Transfer Batch**: Move all items to target location and deactivate
- **Cancel Batch**: Remove all items from batch and deactivate

## Location System Changes

### Before
- Location was a free-text field
- Users could enter any location value

### After
- Location is now a dropdown with two options:
  - **Storage**: For items kept in storage
  - **Show**: For items displayed at shows/events
- Existing items with invalid locations are automatically set to "Storage"

## Frontend Changes

### New UI Elements
- **Batch Management Section**: New card with batch controls
- **Active Batch Indicator**: Shows currently active batch
- **Create Batch Modal**: Form for creating new batches
- **Batch List Modal**: Shows all batches with status
- **Batch Details Modal**: Shows batch items and actions

### Updated Elements
- **Location Fields**: Changed from text input to dropdown
- **Scan Behavior**: Modified to handle batch scanning
- **Item Forms**: Updated to use new location validation

## Migration

### Running the Migration
```bash
cd card-inventory-app
python migrate_batch_system.py
```

### What the Migration Does
1. Creates the `batches` table if it doesn't exist
2. Adds `batch_id` column to `items` table if it doesn't exist
3. Updates existing items with invalid locations to "Storage"

## Example Use Cases

### Trade Show Preparation
1. Create batch "Trade Show 2024"
2. Set target location to "Show"
3. Scan all items going to the show
4. Transfer batch when ready to display

### Storage Organization
1. Create batch "Storage Reorganization"
2. Set target location to "Storage"
3. Scan items being moved to storage
4. Transfer batch to update all locations

### Event Planning
1. Create batch "Comic Con Items"
2. Set target location to "Show"
3. Scan items for the event
4. Cancel batch if plans change
5. Transfer batch when going to event

## Benefits

### ✅ **Organized Workflows**
- Group related items together
- Plan transfers in advance
- Track items by purpose

### ✅ **Bulk Operations**
- Transfer multiple items at once
- Reduce manual location updates
- Prevent missed items

### ✅ **Error Prevention**
- Visual confirmation of batch contents
- Ability to cancel before transfer
- Clear status indicators

### ✅ **Audit Trail**
- Track when batches were created and transferred
- See which items were in each batch
- Maintain history of operations

## Technical Implementation

### Backend
- **Models**: Added Batch model with relationships
- **Schemas**: Added batch-related Pydantic schemas
- **CRUD**: Added batch management operations
- **Routes**: Added batch API endpoints

### Frontend
- **JavaScript**: Added batch management functions
- **HTML**: Added batch modals and controls
- **CSS**: Reused existing modal styles
- **Event Handling**: Added batch-related event listeners

### Database
- **Migration**: Safe migration script for existing databases
- **Validation**: Location field validation
- **Relationships**: Foreign key constraints
- **Indexes**: Optimized for batch queries

This batch system provides a powerful way to organize and manage inventory transfers while maintaining data integrity and providing a smooth user experience.
