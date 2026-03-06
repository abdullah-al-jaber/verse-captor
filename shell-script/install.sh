#!/bin/sh
URL="https://raw.githubusercontent.com/abdullah-al-jaber/verse-fox/vanilla/python-script/main.py"
DEST_DIR="/usr/bin"
DEST_PATH="$DEST_DIR/verse-fox"

if [ "$(id -u)" -ne 0 ]; then
  echo "[ERROR] Failed to gain root permission !"
  exit 1
fi

curl -sSL "$URL" -o "$DEST_PATH" || { echo "Failed to download the script !"; exit 2; }
chmod +x "$DEST_PATH" || { echo "Failed to make the script executable !"; exit 3; }

echo "Successfully installed the script !"

# Final Version
