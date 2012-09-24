# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
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


from amcat.scraping.scraper import Scraper,ScraperForm

from django import forms
from twitter import TwitterStream,UserPassAuth
from datetime import date
import json
import csv
from sys import argv
import logging; log = logging.getLogger(__name__)
from datetime import timedelta

class TwitterScraper(object):
    """Constantly get tweets from the twitter streaming api """
    username, password = argv[1:]
    lastdate = date.today()
    target = date.today().strftime("tweets/twitter_scrapheap_%Y-%m-%d.csv")
    writer = csv.writer(open(target,'a+'))

    def run(self):
        
        stream = TwitterStream(auth=UserPassAuth(self.username,self.password))
        iterator = stream.statuses.sample()

        
        i = 0
        for tweet in iterator:
            i += 1
            
            self.datecheck()

            data =  self.filter_tweet_data(tweet)
            if(data):
                self.writer.writerow(data)

            if i % 10000 == 0:
                print("Added {} tweets to file {}".format(i,self.target))

        self.run()



    def datecheck(self):
        if self.lastdate != date.today():
            print("\n\nNew date detected, changing target file\n\n")
            self.target = date.today().strftime("tweets/twitter_scrapheap_%Y-%m-%d.csv")
            self.writer = csv.writer(open(self.target,'a+'))
            self.writer.writerow(['id','created at','text','hashtags','urls','user mentions','retweeted','user id','in reply to status id','in reply to user id','place id','user location','user language','contributor id\'s','contributor screen names respectively'])
            self.lastdate = date.today()



    def filter_tweet_data(self,tweet):



        if 'id_str' not in tweet.keys():
            return False

        
        data = [
            tweet['id_str'],
            tweet['created_at'],
            tweet['text'],
            "\n".join([hashtag['text'] for hashtag in tweet['entities']['hashtags']]),
            "\n".join([url['url'] for url in tweet['entities']['urls']]),
            "\n".join([user_mention['id_str'] for user_mention in tweet['entities']['user_mentions']]),
            tweet['retweeted']
            ]
        try:
            data.append(tweet['user']['id_str'])
        except:
            data.append(None)
        try:
            data.append(tweet['in_reply_to_status_id_str'])
            data.append(tweet['in_reply_to_user_id_str'])
        except:
            for x in range(2):
                data.append(" ")

        try:
            data.append(tweet['place']['id_str'])
        except:
            data.append(None)

        if 'location' in tweet['user'].keys():
            data.append(tweet['user']['location'])
        else:
            data.append(" ")

        if 'lang' in tweet['user'].keys():
            data.append(tweet['user']['lang'])
        else:
            data.append(" ")

        try:
            contributors = {'ids':' ','screen_names':' '}
            for contributor in tweet['contributors']:
                contributors['ids'] += (contributor['id_str']+";")
                contributors['screen_names'] += (contributor['screen_name']+";")
            data.append(contributors['ids'])
            data.append(contributors['screen_names'])
        except TypeError:
            pass
        i = 0
        for x in data:
            try:
                data[i] = unicode(x).encode('utf-8')
                
            except:
                pass
            i += 1
        return data





if __name__ == '__main__':
    ts = TwitterScraper()
    ts.run()
