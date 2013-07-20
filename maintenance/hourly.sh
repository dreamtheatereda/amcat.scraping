#!/bin/bash                                                                                          

DATE=$(date +'%Y-%m-%d')
python $PYTHONPATH/scrapers/vienna/orf_at.py $VIENNA_PROJECT $DATE --articleset $ORF_AT_ARTICLESET
python $PYTHONPATH/scrapers/tv/teletekst.py $TELETEKST_PROJECT --articleset $TELETEKST_ARTICLESET
python $PYTHONPATH/scrapers/vienna/kurier.py $VIENNA_PROJECT $DATE --articleset $KURIER_ARTICLESET
python $PYTHONPATH/scrapers/vienna/google_at.py $VIENNA_PROJECT $DATE --articleset $GOOGLE_NEWS_AT_ARTICLESET
wait
DEDUPLICATE='python '$PYTHONPATH'/amcat/scripts/maintenance/deduplicate.py'
$DEDUPLICATE $TELETEKST_ARTICLESET --first_date $DATE --last_date $DATE
$DEDUPLICATE $ORF_AT_ARTICLESET --first_date $DATE --last_date $DATE
$DEDUPLICATE $KURIER_ARTICLESET --first_date $DATE --last_date $DATE
$DEDUPLICATE $GOOGLE_NEWS_AT_ARTICLESET --first_date $DATE --last_date $DATE
wait
kill `ps -ef |grep twitter_statuses_filter|grep -v grep|awk '{print $2}'`
wait
python $PYTHONPATH/scrapers/social/twitter/twitter_statuses_filter.py $DATE
