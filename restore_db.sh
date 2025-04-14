#!/bin/bash

DB_NAME="crisp_database"
DB_USER="postgres"
DB_HOST="127.0.0.1"
DUMP_FILE="database_backups/11_05_25_Christie_10mm_15_04.sql"

# Step 1: Terminate any active connections to the database
echo "Terminating active connections to $DB_NAME..."
psql -U $DB_USER -h $DB_HOST -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"

# Step 2: Drop the database
echo "Dropping the database $DB_NAME..."
dropdb -U $DB_USER -h $DB_HOST $DB_NAME

# Step 3: Recreate the database (if not already created)
echo "Creating the database $DB_NAME..."
psql -U $DB_USER -h $DB_HOST -d postgres -c "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || createdb -U $DB_USER -h $DB_HOST $DB_NAME

# Step 4: Restore the database from the dump file
echo "Restoring the database from $DUMP_FILE..."
psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f $DUMP_FILE

echo "Database restore complete!"
