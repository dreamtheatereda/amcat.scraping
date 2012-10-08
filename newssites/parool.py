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

from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.scraping.document import HTMLDocument

from amcat.tools import toolkit

from urlparse import urljoin
import datetime
import re
from math import fabs

START_URL="http://www.parool.nl"
BASE_URL = "http://www.parool.nl"
PATTERN = "/article/detail/\d+/(\d\d\d\d)/(\d\d)/(\d\d)/"
URLS = []
IGNORE=['photoalbum','verkiezingsuitslagen','weather','article/print','mailFriendForm']

from urllib2 import HTTPError,URLError


class ParoolScraper(HTTPScraper, DatedScraper):
    medium_name = "Parool website"
    def _get_units(self):
        for doc in self.scrape_page(START_URL):
            yield doc

    def scrape_page(self,url,depth=0):
        depth = depth + 1
        if depth < 11:
            print("{} - {}".format(depth,url))
            URLS.append(url)

            p = re.compile(PATTERN)
            _date = p.search(url)
            if _date:
                date = datetime.date(year=int(_date.group(1)),month=int(_date.group(2)),day=int(_date.group(3)))

            if ("article/detail" not in url or date >= self.options['date']):
                try:
                    doc = self.getdoc(url)
                except (HTTPError,URLError,RuntimeError):
                    pass
                else:
                    if _date: 
                        if date == self.options['date']:
                            yield HTMLDocument(url=url,doc=doc)
                    for a in doc.cssselect("a"):
                        nxturl = urljoin(url,a.get('href'))
                        if nxturl not in URLS:
                            if self.validurl(nxturl) == True:
                                for doc in self.scrape_page(nxturl,depth=depth):
                                    yield doc
            
                
    def _scrape_unit(self,page):
        page.prepare(self)
        page.props.headline = page.doc.cssselect("#art_box2 h1.k20")[0].text.strip()
        try:
            page.props.author = page.doc.cssselect("#art_box2")[0].tail.split("(Door: ")[1].rstrip(")")
        except IndexError:
            page.props.author = "redactie"
        page.props.text = page.doc.cssselect("#art_box2")[0].text_content()
        yield page


    def validurl(self,url):
        if 'http://www.parool.nl' in url:
            if not ('photoalbum' in url or 'verkiezingsuitslagen' in url or 'article/print' in url or 'weather' in url or 'mailFriendForm' in url):
                return True
            else:
                return False
        else:
            return False

if __name__ == '__main__':
    import sys
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(ParoolScraper)
