# Calendar Scheduling & Employee Multi-Select Features

This document describes two new features added to the application.

## 1. Calendar-Based Scheduling

### Overview
Employees can now be scheduled using specific calendar dates instead of just recurring days of the week.

### Database Changes
- **Migration**: `2026_03_10_add_calendar_scheduling.py`
- **Table**: `employee_position_schedule`
- **New Columns**:
  - `schedule_type` (TEXT): Either 'recurring' or 'calendar'
  - `specific_dates` (JSON): Array of date strings in YYYY-MM-DD format

### How It Works

**Recurring Schedule (Existing Behavior)**:
- Select days of week: Monday, Tuesday, Wednesday, etc.
- Employee appears in daily balance on those weekdays
- Example: `["Monday", "Wednesday", "Friday"]`

**Calendar Schedule (New Feature)**:
- Select specific dates from calendar picker
- Employee appears only on those exact dates
- Example: `["2026-03-15", "2026-03-22", "2026-03-29"]`

### User Interface

**Employee Form** (`/employees/new` or `/employees/{slug}/edit`):
1. For each position, select schedule type:
   - Radio button: "Recurring Days"
   - Radio button: "Specific Dates"
2. If "Recurring Days": checkboxes for weekdays
3. If "Specific Dates":
   - Date picker input
   - "Add Date" button
   - Date chips showing selected dates (with × to remove)

**Employee List** (`/employees`):
- Recurring schedules show: "Monday, Tuesday, Wednesday"
- Calendar schedules show: "📅 3 specific date(s)" with first 3 dates listed below

### Backend Logic

**Auto-Population** (`app/routes/daily_balance.py:is_employee_scheduled_for_date()`):
```python
def is_employee_scheduled_for_date(schedule, target_date, day_of_week):
    if schedule_type == 'recurring':
        return day_of_week in schedule.days_of_week
    elif schedule_type == 'calendar':
        return target_date_str in schedule.specific_dates
```

The daily balance form automatically populates with employees based on:
- Recurring: Day name matches (e.g., "Monday")
- Calendar: Exact date matches (e.g., "2026-03-15")

## 2. Employee Multi-Select with Checkboxes

### Overview
When adding employees to the daily balance form, users can now select multiple employees at once using checkboxes instead of adding them one at a time from a dropdown.

### Use Cases
- Quickly add multiple employees to a shift
- Bulk-add entire positions
- Save time when setting up daily entries

### How It Works

**Before**:
- Click "Add Employee" button
- Select one employee from dropdown
- Click "Add"
- Repeat for each employee

**After**:
- Click "Add Employee" button
- Check multiple employees in the list
- Use "Select All" / "Deselect All" for convenience
- Click "Add Selected" to add all at once

### User Interface

**Daily Balance Form** (`/daily-balance`):
- "Add Employee" button opens modal
- Modal displays checkbox list grouped by position
- Select All / Deselect All buttons at top
- "Add Selected" button adds all checked employees
- Employees already added are filtered out from the list

**Modal Features**:
- Max height with scrolling for long employee lists
- Position headers to organize employees
- Large checkboxes (18x18px) for easy selection
- Clear visual grouping by position

### Frontend Logic

**Updating Checkbox List** (`updateAddEmployeeCheckboxList()`):
```javascript
// Get currently added employees
const currentComboIds = new Set();
document.querySelectorAll('.employee-id-input').forEach(input => {
    currentComboIds.add(input.value);
});

// Group available employees by position
const employeesByPosition = {};
allEmployees.forEach(emp => {
    if (!currentComboIds.has(emp.combo_id)) {
        if (!employeesByPosition[emp.position.name]) {
            employeesByPosition[emp.position.name] = [];
        }
        employeesByPosition[emp.position.name].push(emp);
    }
});

// Render checkboxes grouped by position
```

**Adding Selected Employees** (`addSelectedEmployees()`):
```javascript
const checkboxes = document.querySelectorAll('.employee-checkbox:checked');

if (checkboxes.length === 0) {
    alert('Please select at least one employee');
    return;
}

checkboxes.forEach(checkbox => {
    const employee = JSON.parse(checkbox.dataset.employee);
    addEmployeeEntry(employee);
});
```

**Select All/Deselect All** (`selectAllEmployees(select)`):
```javascript
const checkboxes = document.querySelectorAll('.employee-checkbox');
checkboxes.forEach(checkbox => {
    checkbox.checked = select; // true or false
});
```

## Migration Notes

Both migrations are designed to be:
- **Idempotent**: Can run multiple times safely
- **Backward Compatible**: Existing data is preserved
- **Defensive**: Check for column existence before adding

### Running Migrations

Migrations run automatically on container startup via `docker-entrypoint.sh`:
```bash
python run_migrations.py
```

Or manually:
```bash
docker exec -it <container> python run_migrations.py
```

### Rollback

To re-run a migration:
```sql
DELETE FROM schema_migrations WHERE id = 'migration_id';
```

Then restart the container or run migrations manually.

## Testing Checklist

### Calendar Scheduling
- [ ] Create employee with recurring schedule
- [ ] Create employee with calendar dates
- [ ] Edit employee to change from recurring to calendar
- [ ] Edit employee to change from calendar to recurring
- [ ] Verify employee list shows correct schedule info
- [ ] Verify daily balance auto-populates correctly for recurring
- [ ] Verify daily balance auto-populates correctly for calendar dates
- [ ] Add/remove calendar dates
- [ ] Test with past, present, and future dates

### Employee Multi-Select
- [ ] Open Add Employee modal
- [ ] Verify employees are grouped by position
- [ ] Check multiple employees from different positions
- [ ] Use "Select All" button
- [ ] Use "Deselect All" button
- [ ] Click "Add Selected" - all checked employees should be added
- [ ] Verify employees are sorted correctly (by position, then name)
- [ ] Re-open modal - added employees should not appear in list
- [ ] Add more employees - verify they integrate correctly
- [ ] Test with finalized report (modal should not be accessible)

## Files Modified

### Calendar Scheduling
- `migrations/2026_03_10_add_calendar_scheduling.py` (new)
- `app/models.py` (EmployeePositionSchedule)
- `app/routes/employees.py` (create/edit routes)
- `app/routes/daily_balance.py` (is_employee_scheduled_for_date)
- `app/templates/employees/form.html` (UI with date picker)
- `app/templates/employees/list.html` (display calendar info)

### Employee Multi-Select
- `app/templates/daily_balance/form.html` (modal UI and JavaScript)
