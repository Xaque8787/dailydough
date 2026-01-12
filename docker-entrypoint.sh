#!/bin/bash
set -e

echo "=========================================="
echo "Starting Internal Management System"
echo "=========================================="

# Display version information
if [ -f /app/.dockerversion ]; then
    VERSION=$(cat /app/.dockerversion)
    echo "Version: $VERSION"
fi

# Ensure data directory exists and has proper permissions
echo "Ensuring data directory exists..."
mkdir -p /app/data

# Check if database exists
if [ ! -f /app/data/database.db ]; then
    echo "Database not found. Running migrations to initialize..."
    python3 /app/run_migrations.py
else
    echo "Database exists. Skipping initial migrations."
    echo "Note: To run migrations manually, use: python3 /app/run_migrations.py"
fi

echo "=========================================="
echo "Starting application..."
echo "=========================================="

# Execute the CMD passed to the container
exec "$@"
