#!/bin/bash

# If I run this in the repo root, postgres command should be port forwarded to database container. So the log file needs to be relative to the local directory only.

# --- Colours ---
GREEN_BG="\e[42m"
RED_BG="\e[41m"
WHITE_TEXT="\e[97m"
RESET="\e[0m"

# --- Config ---
PG_USER="postgres"                 # PostgreSQL user
PG_HOST="127.0.0.1"
PG_DB="crisp_database"         # Replace with your database name
LOG_FILE="./restore_points.log"    # Log file to keep track of all restore points

# --- Usage Check ---
if [[ "$1" != "--name" || -z "$2" ]]; then
  echo "Usage: $0 --name <restore_point_name>"
  exit 1
fi

RESTORE_POINT_NAME="$2"

# --- Create Restore Point ---
if psql -h "$PG_HOST" -U "$PG_USER" -d "$PG_DB" -c "SELECT pg_create_restore_point('$RESTORE_POINT_NAME');"; then
  # --- Log the Restore Point ---
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
  echo "$TIMESTAMP $RESTORE_POINT_NAME" >> "$LOG_FILE"
  echo -e "${GREEN_BG}${WHITE_TEXT}Restore point '$RESTORE_POINT_NAME' created and logged at $TIMESTAMP ${RESET}"
else
  echo -e "${RED_BG}${WHITE_TEXT}Failed to create restore point '$RESTORE_POINT_NAME' ${RESET}"
  exit 2
fi
