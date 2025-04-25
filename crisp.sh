#!/bin/bash

# --- Colours ---
GREEN_BG="\e[42m"
BLUE_BG="\e[44m]"
ORANGE_BG="\e[43m"
RED_BG="\e[41m"
WHITE_TEXT="\e[97m"
RESET="\e[0m"

if [[ -n "$FUNCTIONS_LOADED" ]]; then
    echo "CRISP functions already exist."
    return
fi

# Define functions instead of aliases
crisp() {
    echo -e "${GREEN_BG}${WHITE_TEXT}Starting CRISP...${RESET}"
    docker compose down && docker compose up
}

close_crisp() {
    echo -e "${RED_BG}${WHITE_TEXT}Stopping CRISP...${RESET}"
    docker compose down
}

rebuild_crisp() {
    echo -e "${ORANGE_BG}${WHITE_TEXT}Rebuilding CRISP...${RESET}"
    docker compose down && docker compose up --build
}

export FUNCTIONS_LOADED=1

echo "CRISP functions created!"
