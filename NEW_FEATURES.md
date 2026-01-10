# New Features - Daily Balance CRUD System

## Overview
The Daily Balance page has been significantly enhanced with new features for better flexibility and real-time calculations.

## Key Features

### 1. Real-Time Take-Home Tips Calculation
- **What it does**: The "Take-Home Tips" field now calculates automatically as you type
- **How it works**: Enter values in Bank Card Tips, Cash Tips, Adjustments, and Tips on Paycheck fields
- **Formula**: `Take-Home Tips = Bank Card Tips + Cash Tips + Adjustments - Tips on Paycheck`
- **Benefit**: No need to save draft to see the calculated value

### 2. Tips on Paycheck Field
- **New field**: Added to Employee Entries section
- **Purpose**: Track tips that will be paid through payroll instead of cash
- **Behavior**:
  - Subtracts from Take-Home Tips
  - Automatically appears in Revenue & Income section when value is greater than zero
  - Shows as "[Employee Name] - Tips on Paycheck" in the financial summary
- **Use case**: When an employee requests tips to be added to their paycheck for tax/record purposes

### 3. CRUD Financial Line Items
The Revenue & Income and Deposits & Expenses tables are now fully manageable.

#### What Changed:
- **Before**: Hardcoded list of financial categories
- **After**: Dynamic system with persistent templates

#### Features:
- **Default Templates**: The system comes with all previous categories as default templates
- **Persistence**: Templates persist across all days
- **Day-Specific Values**: Each day stores its own values for each template
- **Employee Tips Integration**: Tips on Paycheck entries are automatically added to Revenue & Income for the specific day
- **Full CRUD Operations**: Admin users can Create, Read, Update, and Delete ALL line items
  - **Add** new items via "⚙ Manage Items" button
  - **Rename** any item (including defaults) using the "✎" button
  - **Remove** any item (including defaults) using the "×" button
- **Inline Editing**: Rename items directly in the table with save/cancel options

#### Current Default Templates:

**Revenue & Income:**
- Cash Drawers Beginning
- Food Sales
- Non Alcohol Beverage Sales
- Beer Sales
- Wine Sales
- Other Revenue
- Catering Sales
- Fundraising Contributions
- Sales Tax Payable
- Gift Certificate Sold

**Deposits & Expenses:**
- Gift Certificate Redeemed
- Checking Account Cash Deposit
- Checking Account Bank Cards
- Cash Paid Out
- Cash Drawers End

## Migration

### For New Installations:
No migration needed. The system will automatically create the correct database structure on first run.

### For Existing Installations:
Run the migration script to transition to the new system:

```bash
python3 migrate_to_crud_system.py
```

This migration will:
1. Create new tables for CRUD financial items
2. Add the tips_on_paycheck column
3. Migrate all existing financial data to the new structure
4. Remove old hardcoded columns
5. Set up default templates

**Important**: Back up your database before running the migration!

```bash
cp data/database.db data/database.db.backup
```

## CSV Reports

CSV reports have been updated to include:
- Complete financial summary with all line items
- Revenue & Income breakdown
- Deposits & Expenses breakdown
- Cash Over/Under calculation
- Tips on Paycheck column in employee breakdown

## Usage Tips

### Daily Balance Entry:
1. Select the date
2. Enter financial line item values (automatically saved with templates)
3. Add employees working that day
4. For each employee, enter:
   - Bank Card Sales
   - Bank Card Tips
   - Total Sales
   - Cash Tips
   - Adjustments (if any)
   - Tips on Paycheck (if applicable)
5. Watch Take-Home Tips calculate in real-time
6. Save Draft or Generate Report

### Tips on Paycheck Workflow:
1. Employee requests $50 in tips on their paycheck
2. Enter 50.00 in the "Tips on Paycheck" field for that employee
3. The system automatically:
   - Subtracts $50 from their Take-Home Tips
   - Adds "$50.00 - [Employee Name] - Tips on Paycheck" to Revenue & Income
   - Includes this in the Cash Over/Under calculation
4. When you Generate Report, this appears in the CSV for accounting records

## How to Use CRUD Financial Items

### Entering Management Mode (Admin Only):
1. Go to the Daily Balance page
2. In either the "Revenue & Income" or "Deposits & Expenses" section, click the "⚙ Manage Items" button
3. This will:
   - Show edit (✎) and delete (×) buttons next to all items
   - Open a dialog to add new items
   - Change the button text to "Add New Item"
4. Click the button again to exit management mode and hide all editing controls

### Adding a New Line Item (Admin Only):
1. Enter management mode by clicking "⚙ Manage Items"
2. In the dialog that appears, enter the name of the new item (e.g., "Liquor Sales")
3. Click "Add Item"
4. The new item will appear in the table and will be available on all future days
5. You can close the dialog using "Close" button and continue editing other items
6. Click "Add New Item" to reopen the dialog

### Renaming a Line Item (Admin Only):
1. Enter management mode by clicking "⚙ Manage Items"
2. Find the item you want to rename
3. Click the blue "✎" (edit) button next to the item name
4. The item name becomes an editable text field
5. Type the new name
6. Click the green "✓" (save) button to save, or gray "✗" (cancel) button to cancel
7. The renamed item will update across all future days

### Removing a Line Item (Admin Only):
1. Enter management mode by clicking "⚙ Manage Items"
2. Find the item you want to remove
3. Click the red "×" button next to the item name
4. Confirm the deletion
5. The item will be removed from all future days (existing data is preserved)

**Note**: You can edit or remove ANY item, including the original defaults. Be careful when deleting items as this affects all future daily balance forms!

## Future Enhancements

Potential additions:
- Reorder line items by drag-and-drop
- Archive unused templates
- Import/export template configurations
