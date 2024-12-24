#!/bin/bash

# This script automatically runs client.py if it exists
# If client.py doesn't exist, this script will setup the file
# This script also keeps client.py updated with the latest version from the repository

# Written and maintained by Felix Gao - proudly open source :)
# Check out the repo at https://github.com/felixgao-0/my-website

# Configuration variables :D (Don't modify these unless smth changes important)
# TODO: REMOVE DEV BRANCH AND REPLACE WITH MAIN BRANCH
FILE_REMOTE_URL="https://raw.githubusercontent.com/felixgao-0/my-website/refs/heads/feat/nest-management-bot/nest-management-bot/client.py"
CLIENT_FILEPATH="$HOME/client.py" # FIXME: replace with $home in prod i beg you :plead-blobhaj-1:
# End configuration variables

remote_file_hash=$(curl -s $FILE_REMOTE_URL | sha256sum)


# write logic here for missing the env file

# Write logic here for not up to date setup file (wait thats this file!)

if [ -f client.py ]; then # Check if the client file exists
    if [ "$(sha256sum "$CLIENT_FILEPATH")" == "$remote_file_hash" ]; then
        echo "client.py exists and matches the remote file"
    else
        echo "client.py is not up to date, updating client.py"
        curl -o "$CLIENT_FILEPATH" "$FILE_REMOTE_URL"
    fi
else # Client doesn't exist, make it exist :D
    echo "client.py does not exist, setting up client.py"
    curl -o "$CLIENT_FILEPATH" "$FILE_REMOTE_URL"
fi


# write logic here for missing venv and installing it + needed dependencies

echo "Running client.py"
# Run the client with the env
nest-management-bot/venv/bin/python3.11 nest-management-bot/client.py
