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

try:
    from amcatscraping.social.twitter.twitter_statuses_user_timeline import TwitterStatusesUserTimelineScraper
except ImportError:
    from scraping.social.twitter.twitter_statuses_user_timeline import TwitterStatusesUserTimelineScraper

import csv
import os

target = os.environ.get('PYTHONPATH')+"/{scraping_module}/social/twitter/users.csv"
if os.path.exists(target.format(scraping_module="scraping")):
    CSV_READ = csv.reader(open(os.environ.get('PYTHONPATH')+'/scraping/social/twitter/users.csv','rb'))
elif os.path.exists(target.format(scraping_module="amcatscraping")):
    CSV_READ = csv.reader(open(os.environ.get('PYTHONPATH')+'/amcatscraping/social/twitter/users.csv','rb'))


import json

CSV_WRITE = csv.writer(open('test.csv','w'))


class TwitterPoliticiScraper(TwitterStatusesUserTimelineScraper):
    medium_name = "Twitter - invloedrijke twitteraars en politici"

    def __init__(self, *args, **kwargs):
        super(TwitterPoliticiScraper, self).__init__(*args, **kwargs)
        self.notfound = open('readme.txt','w')
        self.newlines = []

    def _get_units(self):
        first = True
        for person in CSV_READ:
            if first:
                first = False
                continue

            self.options['user_id'] = None
            try:
                self.options['user_id'] = person[8]
            except IndexError:
                self.options['url'] = person[7]
            self.options['screenname'] = None
            try:
                for unit in super(TwitterPoliticiScraper, self)._get_units():
                    yield unit
            except ValueError: #protected tweets
                pass
            except super(TwitterPoliticiScraper,self).RateLimitError as e:
                print(e)
            
            newline = person
            newline.append(self.options['user_id'])
            self.newlines.append(newline)

        

        self.update_csvfile()

    def update_csvfile(self):
        CSV_WRITE.writerow([1,2,3,4,5,6,7,8])
        for line in self.newlines:
            CSV_WRITE.writerow(line)


                

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TwitterPoliticiScraper)


