# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
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

from amcat.scraping.document import Document
from amcat.scraping.scraper import DatedScraper
import csv
import json

FILE='/home/amcat/tweets/filter_{y:04d}-{m:02d}-{d:02}.csv'
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

from amcat.tools.toolkit import readDate

class TwitterCSVScraper(DatedScraper):
    medium_name = "filtered tweets"

    def __init__(self, *args, **kwargs):
        super(TwitterCSVScraper, self).__init__(*args, **kwargs)

    def _get_units(self):
        index_dict = {
            'y' : self.options['date'].year,
            'm' : self.options['date'].month,
            'd' : self.options['date'].day
        }
        
        le_file = open(FILE.format(**index_dict),'r')
        index = csv.DictReader(le_file,fieldnames=fields)


        while True:
            try:
                nxt = index.next()
            except csv.Error:
                continue
            _tweet = Document()
            if self.options['date'].day == 26:
                _tweet.props.text = nxt[None][14].decode('utf-8')
                _date = nxt[None][4].split(" ")
                try:
                    user = eval(nxt['current_user_retweet'])['screen_name']
                except SyntaxError:
                    continue
            
            elif self.options['date'].day == 28:
                _date = nxt[None][0].split(" ")
                _tweet.props.text = nxt[None][13].decode('utf-8')
                try:
                    user = eval(nxt['annotations'])['screen_name']
                except SyntaxError:
                    continue
            else:
                _tweet.props.text = nxt['text'].decode('utf-8')
                _date = nxt['created_at'].split(" ")
                try:
                    user = eval(nxt['user'])['screen_name']
                except SyntaxError:
                    continue
            _tweet.props.author = user
            _date = " ".join([_date[2],_date[1],_date[-1]])
            _tweet.props.date = readDate(_date).date()
            _tweet.props.alldata = nxt
            _tweet.props.text = "{}: {}".format(_tweet.props.author,_tweet.props.text)
            print(_tweet.props.text)

            
            yield _tweet

        
    def _scrape_unit(self, tweet): 
        yield tweet
        




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TwitterCSVScraper)


