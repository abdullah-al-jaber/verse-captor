#!/bin/sh
MAIN_NAME="verse-captor"
SERVER_URL="https://abdullah-al-jaber.github.io/$MAIN_NAME/server-script/main.py"
USER_URL="https://abdullah-al-jaber.github.io/$MAIN_NAME/user-script/main.js"
MAIN_COMPLETION_URL="https://abdullah-al-jaber.github.io/$MAIN_NAME/shell-script/completion.fish"
SERVER_PATH="/usr/bin/$MAIN_NAME"
USER_PATH="/android/$MAIN_NAME.js"
MAIN_COMPLETION_PATH="/etc/fish/completions/$MAIN_NAME.fish"

[ "$(id -u)" -eq 0 ] || {
    echo "Please execute with root privilege !" && exit
}

curl -sSL "$SERVER_URL" -o "$SERVER_PATH" || {
    echo "FAILURE: curl \"$SERVER_URL\" -o \"$SERVER_PATH\" !" && exit
}
chmod +x "$SERVER_PATH" || {
    echo "FAILURE: chmod +x \"$SERVER_PATH\" !" && exit
}

curl -sSL "$MAIN_COMPLETION_URL" -o "$MAIN_COMPLETION_PATH" || {
    echo "FAILURE: curl \"$MAIN_COMPLETION_URL\" -o \"$MAIN_COMPLETION_PATH\" !" && exit
}

curl -sSL "$USER_URL" -o "$MAIN_NAME.js" || {
    echo "FAILURE: curl \"$USER_URL\" -o \"$MAIN_NAME.js\" !" && exit
}
mv "$MAIN_NAME.js" "$USER_PATH" 2>/dev/null || {
    USER_PATH="/$(pwd)/$MAIN_NAME.js"
}

echo "SUCCESS: ALL DONE !"
echo "Please install user script ! PATH: \"$USER_PATH\" !"
