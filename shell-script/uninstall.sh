#!/bin/sh
DEST_DIR="/usr/bin"
DEST_PATH="$DEST_DIR/verse-fox"

if [ "$(id -u)" -ne 0 ]; then
  echo "Failed to gain root permission !"
  exit 1
fi

rm $DEST_PATH || { echo "Failed to remove the script !"; exit 2; }
echo "Successfully uninstalled the script !"

# Final Version
