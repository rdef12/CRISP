#!/bin/bash
set -eu

echo "wal_level = logical" >> /var/lib/postgresql/data/postgresql.conf
echo "Restarting PostgreSQL..."
pg_ctl -D /var/lib/postgresql/data/ restart


echo "Create database and add roles to emulate a new RDS instance"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE $DB_NAME;
    CREATE ROLE rds_iam;
    CREATE ROLE rds_replication REPLICATION;
EOSQL

function for_each_file() {
    DBNAME="$1"
    for file in $2
    do
        psql --echo-all -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DBNAME" -f "$file"
    done
}

# for_each_file "$DB_NAME" "/sql/init/*.sql"
# for_each_file "$DB_NAME" "/sql/migrations/*.sql"

for_each_file "$DB_NAME" "/dev-sql/*.sql"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
select update_user_passwords('$POSTGRES_PASSWORD');
EOSQL