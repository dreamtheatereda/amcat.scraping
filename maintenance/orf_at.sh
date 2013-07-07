#!/bin/bash

DATE=$(date -d 'yesterday' +'%Y-%m-%d')
python $PYTHONPATH/amcat/scraping/vienna/orf_at.py $ORF_AT_PROJECT $DATE --articlese $ORF_AT_ARTICLESET
