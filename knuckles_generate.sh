#!/bin/sh
# $1 is token
# $2 is output
if [ $# -ne 2 ]; then
    echo "usage: knuckles_generate.sh bot_token output_image"
    exit
fi
./bot_message_extractor.py $1 188453877438218240 | ./knuckles_history_mapper.py $2