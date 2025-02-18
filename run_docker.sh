#!/bin/bash

# Define ANSI color codes
GREEN_BG="\e[42m"
WHITE_TEXT="\e[97m"
RESET="\e[0m"

# Print the green block with white text
echo -e "${GREEN_BG}${WHITE_TEXT}       CRISP GUI       ${RESET}"

# Start Docker Compose
docker compose -f /home/lewisdean22/proton_beam_monitor_testing/docker_testing/compose.yaml up -d

# Wait for services to start
sleep 1

# Open browser
powershell.exe /c start http://localhost:3000 &

# Keep Bash running (acts like your working setup)
exec bash
