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

consumer_key="XC92JObeStin0qEHuu08KQ"
consumer_secret="UkEZhOEPI0Ydft85PDF3S2KLrV2AlhZqXMtGVnNSEAc"
access_token="816243289-14u7zplDIiAkTf1fomp9ZUg62eDlzFspXXZv9bty"
access_token_secret="0FncNCYPgBfQvzwqV0a0kJ7Orr4mQUFsDwkPkrCvo"

fields = [
    'annotations',
    'contributors',
    'coordinates',
    'created_at',
    'current_user_retweet',
    'entities',
    'favorited',
    'geo',
    'id',
    'id_str',
    'in_reply_to_screen_name',
    'in_reply_to_status_id',
    'in_reply_to_status_id_str',
    'in_reply_to_user_id',
    'in_reply_to_user_id_str',
    'place',
    'possibly_sensitive',
    'scopes',
    'retweet_count',
    'retweeted',
    'source',
    'text',
    'truncated',
    'user',
    'witheld_copyright',
    'witheld_in_countries',
    'witheld_scope',
    'retweeted_status',
    'possibly_sensitive_editable',
    'limit',
    'disconnect'
    ]



class TwitterFilterForm(forms.Form):
    track_file = forms.CharField(required=False)
    date = forms.DateField()

class TwitterFilterScript(Script):
    options_form = TwitterFilterForm

    def __init__(self,*args,**kargs):
        super(TwitterFilterScript, self).__init__(*args, **kargs)

    def run(self, _input):
        if len(self.options['track_file'])<=1:
            if path.exists(environ.get('PYTHONPATH')+"scraping"):
                self.options['track_file']='{}scraping/social/twitter/track.txt'.format(environ.get('PYTHONPATH'))
            else:
                self.options['track_file']='{}amcatscraping/social/twitter/track.txt'.format(environ.get('PYTHONPATH'))
        words = []
        word_file = open(self.options['track_file'])
        for l in word_file.readlines():
            if not l.startswith("#"):
                [words.append(w.strip()) for w in l.strip("\n").split(",") if len(w.strip())>1]

        print(words)
        s = self.stream()
        s.retry_time = (60*10)
        s.filter(None,words)
        

    def stream(self):
        auth = OAuthHandler(consumer_key,consumer_secret)
        auth.set_access_token(access_token,access_token_secret)
        l = Listener(self.options['date'])
        stream = Stream(auth,l)
        l.stream = stream
        return stream



class Listener(StreamListener):

    def __init__(self,date):
        f = "{}tweets/{}".format(environ.get('PYTHONPATH'),date.strftime("filter_%Y-%m-%d.csv"))
        outputfile = open(f,'a+')
        self.writer = csv.DictWriter(outputfile,fieldnames=fields)


    def on_data(self,data):
        print("tweet found")
        data = json.loads(data)
        if 'limit' in data.keys():
            sleep(10)
        _data = self.dict_unicode_to_str(data)
        for k,v in _data.items():
            if k=='disconnect':
                sleep(10*60)
            if k not in fields:
                return
        self.writer.writerow(_data)
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

    def on_error(status):
        print(status)

    





if __name__ == '__main__':
    from amcat.scripts.tools import cli
    cli.run_cli(TwitterFilterScript)
