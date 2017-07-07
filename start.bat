@echo off
REM This script has not yet been tested on a windows environment.

if exist config.json (
    python3 eventbot.py
) else (
    echo "{" > config.json
    echo "    \"token\": \"insert here\"," >> config.json
    echo "" >> config.json
    echo "    \"sql:\": {" >> config.json
    echo "        \"host\": \"localhost\"," >> config.json
    echo "        \"user\": \"username\"," >> config.json
    echo "        \"pass\": \"password\"" >> config.json
    echo "    }" >> config.json
    echo "}" >> config.json

    echo "config.json generated! Please modify it before running."
)
