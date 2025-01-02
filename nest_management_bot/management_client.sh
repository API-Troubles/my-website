#!/bin/bash

# This script automatically runs client.py if it exists
# If client.py doesn't exist, this script will setup the file
# This script also keeps client.py updated with the latest version from the repository

# Don't modify this script, it will be overwritten next time it runs

# Written and maintained by Felix Gao - proudly open source :)
# Check out the repo at https://github.com/felixgao-0/my-website

# Configuration variables :D (Don't modify unless important)
# TODO: REMOVE DEV BRANCH AND REPLACE WITH MAIN BRANCH
CLIENT_REMOTE_URL="https://raw.githubusercontent.com/felixgao-0/my-website/refs/heads/feat/nest-management-bot/nest_management_bot/client.py"
CLIENT_FILEPATH="./nest_management_bot/client.py"

SERVICE_REMOTE_URL="https://raw.githubusercontent.com/felixgao-0/my-website/refs/heads/feat/nest-management-bot/nest_management_bot/service_file_template.txt"
SERVICE_FILEPATH="./.config/systemd/user/nest_management_bot.service"

# Yes I shoved all my requirements on a single line of bash, oh welp :pf:
DEPENDENCIES=("psutil" "websockets" "humanize" "python-dotenv" "dbus-python")
# END configuration variables

client_remote_hash=$(curl -s CLIENT_REMOTE_URL | sha256sum | cut -d ' ' -f 1)
service_remote_hash=$(curl -s SERVICE_REMOTE_URL | sha256sum | cut -d ' ' -f 1)


colour_echo () {
    # Syntax: colour_echo <message> <colour>
    if [ "$2" == "red" ]; then
        # I shoved error handling here cause why else use red? (famous last words)
        echo -e "\033[31m$1\033[0m" >&2
        exit 1
    elif [ "$2" == "green" ]; then
        echo -e "\033[32m$1\033[0m"
    elif [ "$2" == "yellow" ]; then
        echo -e "\033[33m$1\033[0m"
    fi
}


if [ ! -f "./.env.nest-management-bot" ]; then
    colour_echo "Before you run this setup script make sure you run the token setup script" "red"
fi

if [ ! -d "./nest_management_bot" ]; then
    mkdir ./nest_management_bot
    echo "Folder didn't exist, created ./nest_management_bot/"
fi


if [ -f $SERVICE_FILEPATH ]; then
    if [ "$(sha256sum "$SERVICE_FILEPATH" | cut -d ' ' -f 1)" = "$service_remote_hash" ]; then
        echo "Setup: Systemd service file exists and is up to date"
    else
        echo "Setup: Systemd service file is not up to date, updating nest_management_bot.service"
        curl -o "$SERVICE_FILEPATH" "$SERVICE_REMOTE_URL"
        systemctl --user daemon-reload
    fi
else
    echo "Systemd service file doesn't exist, creating nest_management_bot.service"
    curl -o "$SERVICE_FILEPATH" "$SERVICE_REMOTE_URL"
    systemctl --user daemon-reload
    systemctl --user enable nest_management_bot.service
    systemctl --user start nest_management_bot.service
    echo "Setup: Exiting as the service file was created... bot is running from the service file now"
    colour_echo "Hint: Check systemctl --user status nest_management_bot.service\u001b" "yellow"
    exit 0
fi


if [ -f $CLIENT_FILEPATH ]; then # Check if client file exists
    if [ "$(sha256sum "$CLIENT_FILEPATH" | cut -d ' ' -f 1)" = "$client_remote_hash" ]; then
        echo "Setup: client.py exists and is up to date"
    else
        echo "Setup: client.py is not up to date, updating client.py"
        curl -o "$CLIENT_FILEPATH" "$CLIENT_REMOTE_URL"
    fi
else # Client doesn't exist, make it exist :D
    echo "Setup: client.py does not exist, setting up client.py"
    curl -o "$CLIENT_FILEPATH" "$CLIENT_REMOTE_URL"
fi


if [ -f "nest_management_bot/venv/bin/activate" ]; then
    echo "Setup: Virtual environment exists"
else
    echo "Setup: Virtual environment does not exist, setting up a venv"
    python3 -m venv ./nest_management_bot/venv
    source ./nest_management_bot/venv/bin/activate
    pip install "${DEPENDENCIES[@]}"
    deactivate
fi


colour_echo "Running client.py... finally!" "green"
exec nest_management_bot/venv/bin/python3.11 nest_management_bot/client.py