#!/bin/bash                                                                                          

DATE=$(date +'%Y-%m-%d')
python $PYTHONPATH/scraping/teletekst.py $TELETEKST_PROJECT --articleset $TELETEKST_ARTICLESET
python $PYTHONPATH/scraping/vienna/orf_at.py $ORF_AT_PROJECT $DATE --articleset $ORF_AT_ARTICLESET
wait
python $PYTHONPATH/amcat/scripts/maintenance/deduplicate.py $TELETEKST_ARTICLESET
python $PYTHONPATH/amcat/scripts/maintenance/deduplicate.py $ORF_AT_ARTICLESET
wait
kill `ps -ef |grep twitter_statuses_filter|grep -v grep|awk '{print $2}'`
wait
python $PYTHONPATH/scraping/social/twitter/twitter_statuses_filter.py $DATE
