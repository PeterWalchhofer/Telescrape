#!/bin/sh

. venv/bin/activate
cd ./channelscraper

if [ $# -eq 0 ]
  then
    python3 app.py 
  else 
    if [ $1 == "meta" ]; then
    python3 scrapeChannelMetadata.py 
    fi
fi

deactivate