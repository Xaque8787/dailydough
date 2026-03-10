# Calendar Scheduling & Checkbox Multi-Select Features

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

## 2. Checkbox Multi-Select for Tip Requirements

### Overview
Tip requirements that have `record_data=true` and `no_input=true` now render as checkboxes instead of text labels, allowing multi-select tracking per employee per day.

### Database Changes
- **Migration**: `2026_03_10_add_checkbox_multiselect.py`
- **Table**: `daily_employee_entries`
- **New Column**:
  - `selected_checkboxes` (JSON): Array of field_name slugs

### Use Cases
- Attendance markers
- Shift type indicators
- Special conditions
- Custom boolean attributes per employee

### How It Works

**Configuration** (Tip Requirements setup):
1. Create a tip requirement
2. Set `record_data = true`
3. Set `no_input = true`
4. The requirement will render as a checkbox

**Rendering Logic**:
```python
if req.record_data and req.no_input:
    # Render as checkbox
elif not req.no_input:
    # Render as numeric input
else:
    # Render as text label
```

### User Interface

**Daily Balance Form**:
- Checkboxes appear alongside numeric tip inputs
- Each checkbox has employee's combo_id (employee_id-position_id)
- Styled with larger size (18x18px) for easy clicking
- Disabled when viewing finalized reports

**Data Storage**:
```json
{
  "selected_checkboxes": ["field_slug_1", "field_slug_2"]
}
```

### Backend Logic

**Saving Checkboxes** (`app/routes/daily_balance.py:save_daily_balance_data()`):
```python
selected_checkboxes = []
for req in position.tip_requirements:
    if req.record_data and req.no_input:
        checkbox_key = f"checkbox_{req.field_name}_{combo}"
        if form_data.get(checkbox_key) == "1":
            selected_checkboxes.append(req.field_name)

entry = DailyEmployeeEntry(
    ...
    selected_checkboxes=selected_checkboxes,
    ...
)
```

**Checking Selection** (`app/models.py:DailyEmployeeEntry.is_checkbox_selected()`):
```python
def is_checkbox_selected(self, field_name: str) -> bool:
    if self.selected_checkboxes and isinstance(self.selected_checkboxes, list):
        return field_name in self.selected_checkboxes
    return False
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

### Checkbox Multi-Select
- [ ] Create tip requirement with record_data=true and no_input=true
- [ ] Verify checkbox renders in daily balance form
- [ ] Check/uncheck boxes for different employees
- [ ] Save draft and verify checkboxes persist
- [ ] Finalize report and verify checkboxes are saved
- [ ] View finalized report - checkboxes should be disabled but show state
- [ ] Edit finalized report - checkboxes should be editable
- [ ] Add employee dynamically and verify checkbox appears

## Files Modified

### Calendar Scheduling
- `migrations/2026_03_10_add_calendar_scheduling.py` (new)
- `app/models.py` (EmployeePositionSchedule)
- `app/routes/employees.py` (create/edit routes)
- `app/routes/daily_balance.py` (is_employee_scheduled_for_date)
- `app/templates/employees/form.html` (UI with date picker)
- `app/templates/employees/list.html` (display calendar info)

### Checkbox Multi-Select
- `migrations/2026_03_10_add_checkbox_multiselect.py` (new)
- `app/models.py` (DailyEmployeeEntry)
- `app/routes/daily_balance.py` (save checkbox data)
- `app/templates/daily_balance/form.html` (render checkboxes)
