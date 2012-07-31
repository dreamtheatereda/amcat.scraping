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

import logging; log = logging.getLogger(__name__)

class TwitterForm(ScraperForm):
    track = forms.CharField(max_length=8192, required=False)
    follow = forms.CharField(max_length=8192, required=False)
    username = forms.CharField()
    password = forms.CharField()

class TwitterScraper(Scraper):
    """Constantly get tweets from the twitter streaming api """
    options_form = TwitterForm
    medium_name = "Twitter"

    def __init__(self, options):
        super(TwitterScraper, self).__init__(options)

    def run(self, options):
        
        
        stream = TwitterStream(auth=UserPassAuth(self.options['username'],self.options['password']))
        iterator = stream.statuses.sample()
        for tweet in iterator:
            target = date.today().strftime("twitter_scrapheap_%Y-%m-%d.txt")
            target_file = open(target,'a+')
            try:
                target_file.write(tweet['text']+"\n")
            except:continue
            log.info("Adding tweet to file {target}".format(target=target))
        
        

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    cli.run_cli(TwitterScraper)
