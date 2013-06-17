#!/bin/bash                                                                                           
DATE=$(date +'%Y-%m-%d')
python $PYTHONPATH/scraping/teletekst.py --articleset 22842 258 $DATE [] []
wait
kill `ps -ef |grep _twitter|grep -v grep|awk '{print $2}'`
wait
python $PYTHONPATH/scraping/social/_twitter.py amcat3 nieuwsmonitor
