#!/bin/bash

DATE=$(date -d 'yesterday' +'%Y-%m-%d')
cd $PYTHONPATH
hg up -C trunk
cd $PYTHONPATH/scrapers
hg up -C trunk
wait
python $PYTHONPATH/amcat/scripts/maintenance/daily.py $DATE --deduplicate True 2>&1
wait
python $PYTHONPATH/amcat/scripts/maintenance/scraping_check.py $DATE $SCRAPING_CHECK_MAIL