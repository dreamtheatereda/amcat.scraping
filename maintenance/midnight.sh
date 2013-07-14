#!/bin/bash

DATE=$(date -d 'yesterday' +'%Y-%m-%d')
python $PYTHONPATH/scrapers/vienna/krone.py $KRONE_PROJECT $DATE --articleset $KRONE_ARTICLESET