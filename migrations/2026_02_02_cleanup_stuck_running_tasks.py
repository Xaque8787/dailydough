"""
Migration: Cleanup stuck running task executions

This migration marks all task executions that are stuck in 'running' state as 'failed'
with an appropriate error message. Tasks should not remain in running state indefinitely.
"""

MIGRATION_ID = "2026_02_02_cleanup_stuck_running_tasks"

def upgrade(conn, column_exists, table_exists):
    """
    Update all task executions stuck in 'running' state to 'failed'.
    Sets completed_at to CURRENT_TIMESTAMP and adds an error message.
    """
    cursor = conn.cursor()

    # Check if task_executions table exists
    if not table_exists('task_executions'):
        print("  ℹ️  task_executions table doesn't exist, skipping")
        return

    # Count how many stuck executions exist
    cursor.execute("SELECT COUNT(*) FROM task_executions WHERE status = 'running'")
    count = cursor.fetchone()[0]

    if count == 0:
        print("  ℹ️  No stuck task executions found")
        return

    # Update executions that are stuck in 'running' state
    cursor.execute("""
        UPDATE task_executions
        SET status = 'failed',
            completed_at = CURRENT_TIMESTAMP,
            error_message = 'Task was stuck in running state - likely crashed or database connection issue'
        WHERE status = 'running'
    """)

    print(f"  ✓ Marked {count} stuck task execution(s) as failed")
