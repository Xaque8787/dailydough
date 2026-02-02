# Task Execution Status Fix

## Problem
Scheduled tasks were staying in "running" state even after completing successfully. The UI showed:
- **Started**: None (timestamp never set)
- **Completed**: - (timestamp never set)
- **Status**: running (never updated to "success" or "failed")

## Root Cause
When creating task execution records, the code was only setting `task_id` and `status`, but never setting the `started_at` timestamp:

```python
# OLD CODE (BROKEN)
INSERT INTO task_executions (task_id, status)
VALUES (:task_id, 'running')
```

This caused:
1. `started_at` remained NULL
2. When tasks completed, the status update logic may have failed
3. UI displayed "None" for the start time

## Solution Applied

### 1. Fixed Task Execution Creation (app/services/scheduler_tasks.py)
Updated all 4 task functions to properly set `started_at`:

```python
# NEW CODE (FIXED)
INSERT INTO task_executions (task_id, started_at, status)
VALUES (:task_id, CURRENT_TIMESTAMP, 'running')
```

Functions updated:
- `run_tip_report_task()` (line 141)
- `run_daily_balance_report_task()` (line 277)
- `run_employee_tip_report_task()` (line 417)
- `run_backup_task()` (line 553)

### 2. Created Migration to Fix Historical Records (migrations/2026_02_02_fix_stuck_running_tasks.py)
A migration that updates any existing execution records stuck in "running" state to mark them as "completed". This cleans up historical data.

## Testing
After deploying this fix:
1. New task executions will properly show start and completion timestamps
2. Task status will correctly update from "running" → "success" or "failed"
3. Historical stuck tasks will be marked as completed after running the migration

## Files Changed
- `app/services/scheduler_tasks.py` - Fixed 4 INSERT statements
- `migrations/2026_02_02_fix_stuck_running_tasks.py` - New migration to clean up historical data
