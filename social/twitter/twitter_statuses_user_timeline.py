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

import tweepy
from amcat.scraping.document import Document
from amcat.scraping.scraper import 
from urllib2 import HTTPError

class Options(

class TwitterStatusesUserTimelineScraper(HTTPScraper,DBScraper):
    medium_name = "Twitter"

    def __init__(self, *args, **kwargs):
        super(TwitterStatusesUserTimelineScraper, self).__init__(*args, **kwargs)

        if not (self.options['user_id'] or self.options['screenname'] or self.options['url']):
            raise ValueError("supply either a screen name, an url or a user id")

        elif (not self.options['user_id']):
            if not self.options['url']:
                self.options['url'] = "https://twitter.com/{}".format(self.options['screenname'])
            self.options['user_id'] = self.get_user_id(self.options['url'])

    def get_user_id(self, url):
        try:
            doc = self.getdoc(url)
        except HTTPError:
            raise ValueError("url {} not found")
        
                      
    
