#!/bin/bash
set -e

echo "=========================================="
echo "Starting Internal Management System"
echo "=========================================="

# Display version information
if [ -f .dockerversion ]; then
    VERSION=$(cat .dockerversion)
    echo "Version: $VERSION"
fi

# Ensure data directory exists and has proper permissions
echo "Ensuring data directory exists..."
mkdir -p data

# Always initialize the database schema first (create_all is a no-op on existing tables)
echo "Initializing database schema..."
python3 -c "from app.database import init_db; init_db(); print('Schema initialized.')"

# Always run migrations to apply any incremental changes
echo ""
echo "Checking for database migrations..."
python3 run_migrations.py

echo "=========================================="
echo "Starting application..."
echo "=========================================="

# Execute the CMD passed to the container
exec "$@"
