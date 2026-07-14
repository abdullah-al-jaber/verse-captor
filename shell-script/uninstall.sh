#!/bin/sh
MAIN_NAME="verse-captor"
SERVER_PATH="/usr/bin/$MAIN_NAME"
USER_PATH="/android/$MAIN_NAME.js"
MAIN_COMPLETION_PATH="/etc/fish/completions/$MAIN_NAME.fish"

[ "$(id -u)" -eq 0 ] || {
    echo "Please execute with root privilege !" && exit
}

rm "$SERVER_PATH" || {
    echo "FAILURE: rm \"$USER_PATH\" !" && exit
}

rm "$MAIN_COMPLETION_PATH" || {
    echo "FAILURE: rm \"$MAIN_COMPLETION_PATH\" !" && exit
}

rm "$USER_PATH" "$MAIN_NAME.js" || {
    echo "FAILURE: rm \"$USER_PATH\" \"$MAIN_NAME.js\" !" && exit
}

echo "SUCCESS: ALL DONE !"
