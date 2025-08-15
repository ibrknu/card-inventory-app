# Quantity Update Feature

## Overview

Added a new popup modal that appears when scanning an existing item, allowing users to specify whether they're adding items to inventory or selling items from inventory, along with the quantity to add or subtract.

## Problem Solved

Previously, when scanning an existing item, the system would automatically increment the quantity by 1. This was problematic because:
- Users couldn't specify how many items they were adding
- Users couldn't indicate they were selling items (which should decrease quantity)
- No flexibility in quantity management

## New Feature

### Backend Changes

#### New Endpoint: `/api/items/update-quantity`

**Purpose**: Updates item quantity based on user-specified action and amount

**Request Body**:
```json
{
  "barcode": "1234567890123",
  "action": "add",  // or "sell"
  "quantity": 5
}
```

**Response**: Updated item with new quantity

**Features**:
- ✅ Validates that quantity is greater than 0
- ✅ Prevents selling more items than available in inventory
- ✅ Supports both "add" and "sell" actions
- ✅ Creates scan event for tracking

#### Modified Endpoint: `/api/scan`

**Changes**:
- No longer automatically increments quantity for existing items
- Returns existing item data for frontend to handle quantity updates
- Still creates basic items for new barcodes

#### New Schema: `QuantityUpdateRequest`

```python
class QuantityUpdateRequest(BaseModel):
    barcode: str
    action: str = Field(..., description="Action to perform: 'add' or 'sell'")
    quantity: int = Field(..., gt=0, description="Number of items to add or sell")
```

### Frontend Changes

#### New Modal: Quantity Update Modal

**Features**:
- ✅ Shows item details (barcode, name, current quantity)
- ✅ Radio buttons for "Add to Inventory" or "Sell from Inventory"
- ✅ Quantity input field
- ✅ Validation to prevent negative quantities
- ✅ Clear visual distinction between add (green) and sell (red) actions

**Modal Content**:
- Item barcode
- Item name
- Current quantity
- Action selection (Add/Sell)
- Quantity input
- Update and Cancel buttons

#### Modified Scan Flow

**New Flow**:
1. User scans barcode
2. If item exists:
   - Show quantity update modal
   - User selects action (add/sell) and quantity
   - System updates inventory accordingly
3. If item is new:
   - Show new item modal (existing behavior)
   - User fills in item details

#### JavaScript Functions Added

- `showQuantityUpdateModal(barcode, itemName, currentQuantity)`
- `closeQuantityUpdateModal()`
- `updateItemQuantity(formData)`

## User Experience

### Scanning Existing Items

1. **Scan barcode** of existing item
2. **Modal appears** showing:
   - Item information
   - Current quantity
   - Action options (Add/Sell)
   - Quantity input
3. **Select action**:
   - ➕ **Add to Inventory**: Increases quantity
   - 💰 **Sell from Inventory**: Decreases quantity
4. **Enter quantity** to add or sell
5. **Click "Update Inventory"** to confirm
6. **Success message** shows new quantity

### Validation

- ✅ Quantity must be greater than 0
- ✅ Cannot sell more items than available
- ✅ Clear error messages for invalid actions
- ✅ Prevents overselling with helpful error message

### Visual Feedback

- **Green styling** for "Add to Inventory" action
- **Red styling** for "Sell from Inventory" action
- **Success messages** show action performed and new quantity
- **Error messages** for validation failures

## Example Usage

### Adding Items
1. Scan existing card
2. Select "Add to Inventory"
3. Enter quantity: 3
4. Result: Quantity increases by 3

### Selling Items
1. Scan existing card (current qty: 10)
2. Select "Sell from Inventory"
3. Enter quantity: 2
4. Result: Quantity decreases to 8

### Preventing Overselling
1. Scan existing card (current qty: 5)
2. Select "Sell from Inventory"
3. Enter quantity: 10
4. Result: Error message "Cannot sell more items than available in inventory"

## Benefits

- ✅ **Flexible inventory management** - Add or sell any quantity
- ✅ **Prevents overselling** - Validates available inventory
- ✅ **Clear user interface** - Intuitive radio button selection
- ✅ **Detailed feedback** - Shows current and new quantities
- ✅ **Audit trail** - Creates scan events for all quantity changes
- ✅ **Backward compatibility** - New items still work as before

## Files Modified

### Backend
- `app/routes/scan.py` - Added quantity update endpoint, modified scan endpoint
- `app/schemas.py` - Added QuantityUpdateRequest schema

### Frontend
- `app/static/index.html` - Added quantity update modal, JavaScript functions, event handlers

## Testing

The feature includes comprehensive validation:
- ✅ Adding quantities works correctly
- ✅ Selling quantities works correctly
- ✅ Overselling is prevented
- ✅ Invalid quantities are rejected
- ✅ Modal displays correctly for existing items
- ✅ New items still show the original modal

This feature significantly improves the inventory management workflow by providing precise control over quantity changes while maintaining data integrity and preventing common inventory errors.
