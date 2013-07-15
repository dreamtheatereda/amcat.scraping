#!/bin/bash

DATE=$(date -d 'yesterday' +'%Y-%m-%d')
python $PYTHONPATH/scrapers/vienna/krone.py $VIENNA_PROJECT $DATE --articleset $KRONE_ARTICLESET