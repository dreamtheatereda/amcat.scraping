###########################################################################
#          (C) Vrije Universiteit, Amsterdam (the Netherlands)            #
#                                                                         #
# This file is part of AmCAT - The Amsterdam Content Analysis Toolkit     #
#                                                                         #
# AmCAT is free software: you can redistribute it and/or modify it under  #
# the terms of the GNU Affero General Public License as published by the  #
# Free Software Foundation, either version 3 of the License, or (at your  #
# option) any later version.                                              #
#                                                                         #
# AmCAT is distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
# You should have received a copy of the GNU Affero General Public        #
# License along with AmCAT.  If not, see <http://www.gnu.org/licenses/>.  #
###########################################################################

"""
Script to be run continuously with possibly several sets of arguments, filtering tweets
"""

from django import forms
from amcat.scripts.script import Script
from tweepy import OAuthHandler,Stream
from tweepy.streaming import StreamListener
from os import environ,path
import csv
from datetime import date
import httplib
import json
from time import sleep
import logging; log = logging.getLogger(__name__)

consumer_key="XC92JObeStin0qEHuu08KQ"
consumer_secret="UkEZhOEPI0Ydft85PDF3S2KLrV2AlhZqXMtGVnNSEAc"
access_token="816243289-14u7zplDIiAkTf1fomp9ZUg62eDlzFspXXZv9bty"
access_token_secret="0FncNCYPgBfQvzwqV0a0kJ7Orr4mQUFsDwkPkrCvo"

try:
    from amcatscraping.social.twitter.csv_scraper import fields
except ImportError:
    from scraping.social.twitter.csv_scraper import fields


class TwitterFilterForm(forms.Form):
    query_file = forms.CharField(required=False)
    date = forms.DateField()

class TwitterFilterScript(Script):
    options_form = TwitterFilterForm

    def run(self, _input):
        if not self.options['query_file']:
            self.options['query_file'] = '{}/scraping/social/twitter/filter_query.txt'.format(environ.get('PYTHONPATH'))
        words = []
        word_file = open(self.options['query_file'])
        for l in word_file.readlines():
            if not l.startswith("#"):
                [words.append(w.strip()) for w in l.strip("\n").split(",") if len(w.strip())>1]
        log.info("Starting tweet scraping with the following words:\n{words}".format(**locals()))
        sleep(2)
        s = self.stream()
        s.retry_time = 5
        s.filter(track = words)
        
    def stream(self):
        auth = OAuthHandler(consumer_key,consumer_secret)
        auth.set_access_token(access_token,access_token_secret)
        l = Listener(self.options['date'])
        stream = Stream(auth,l)
        l.stream = stream
        return stream

class Listener(StreamListener):
    def __init__(self,date, *args, **kwargs):
        super(StreamListener, self).__init__(*args, **kwargs)
        f = "/home/amcat/tweets/{}".format(date.strftime("filter_%Y-%m-%d.csv"))
        outputfile = open(f,'a+')
        self.writer = csv.DictWriter(outputfile,fieldnames=fields)

    def on_data(self,data):
        data = self.dict_unicode_to_str(json.loads(data))
        if data['user']['lang'] != 'nl':
            return
        log.info("user '{data[user][id]}' said: \"{data[text]}\"".format(**locals()))
        for k,v in data.items():
            if k=='disconnect':
                sleep(10*60)
            if k not in fields:
                log.warning("'{k}' not in fields:\n{fields}".format(k=k, **globals()))
                del data[k]
                sleep(5)
        
        self.writer.writerow(data)
        return True

    def dict_unicode_to_str(self,data):
        for k,v in data.items():
            if 'unicode' in str(type(v)):            
                data[k] = v.encode('utf-8','replace')
            
            elif 'dict' in str(type(v)):
                data[k] = self.dict_unicode_to_str(v)

            elif 'list' in str(type(v)):            
                data[k] = [str(i).encode('utf-8',errors='replace') for i in v]
           
        return data

    def on_error(self, status):
        print(status)

    





if __name__ == '__main__':
    from amcat.scripts.tools import cli
    cli.run_cli(TwitterFilterScript)
