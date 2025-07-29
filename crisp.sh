#!/bin/bash

# --- Colours ---
GREEN_BG="\033[42m"
BLUE_BG="\033[44m"
ORANGE_BG="\033[43m"
RED_BG="\033[41m"
WHITE_TEXT="\033[97m"
GREEN_TEXT="\033[32m"
RESET="\033[0m"

echo -e "\n${BLUE_BG}${WHITE_TEXT}Available CRISP Functions:${RESET}\n
  ${GREEN_TEXT}crisp${RESET} - Starts the 3 CRISP containers
  ${GREEN_TEXT}close_crisp${RESET} - Stops running the CRISP containers
  ${GREEN_TEXT}rebuild_crisp${RESET} - Rebuild and start CRISP containers

${BLUE_BG}${WHITE_TEXT}Usage:${RESET}

  Source this script in your shell to load the functions, e.g.:
    $ source ./crisp.sh

  Then call the functions directly, e.g.:
    $ crisp
    $ close_crisp
    $ rebuild_crisp
"

if [[ -n "$FUNCTIONS_LOADED" ]]; then
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
