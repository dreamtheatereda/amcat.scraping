 #!/usr/bin/python
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

from __future__ import unicode_literals, print_function, absolute_import

import datetime, sys, urllib, urllib2, re
    
import logging, datetime
from itertools import count

log = logging.getLogger(__name__)

from amcat.scraping.scraper import HTTPScraper
from amcat.models.article import Article
from amcat.tools import toolkit
from amcat.models.medium import get_or_create_medium

PAGEURL = "http://ikregeer.nl/tweets?page=%s"
    
class IkRegeerTweetsScraper(HTTPScraper):
    medium_name = "Twitter (ikregeer.nl)"
    
    def _get_units(self):
        for pagenr in count(1):
            page = PAGEURL % pagenr
            doc = self.getdoc(page)
            for t in doc.cssselect('div."post-container clearfix"'):
                yield t
            if not doc.cssselect("a#pg-next"): break 

 
    def _scrape_unit(self, t):
        author = t.cssselect('a')[0].get('title')
        tweet = t.cssselect('div.entry-summary')[0].text_content()
        date = t.cssselect('span.published')[0].text_content()
        date = datetime.datetime.strptime(date, '%d-%m-%Y').date()
        length = len(filter(None, tweet.split(' ')))
        
        art = Article(headline=tweet, text='', date=date, length=length)
        yield art


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(IkRegeerTweetsScraper)


