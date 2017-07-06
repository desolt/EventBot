#!/bin/bash

if [ ! -f config.json ]; then
    echo "{" >> config.json
    echo "    \"token\": \"insert here\"," >> config.json
    echo "" >> config.json
    echo "    \"sql:\": {" >> config.json
    echo "        \"host\": \"localhost\"," >> config.json
    echo "        \"user\": \"username\"," >> config.json
    echo "        \"pass\": \"password\"" >> config.json
    echo "    }" >> config.json
    echo "}" >> config.json

    echo "config.json generated! Please modify it before running."
else
    python3 eventbot.py
fi
