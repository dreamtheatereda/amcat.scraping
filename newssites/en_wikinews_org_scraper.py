#!/usr/bin/python
# en_wikinews_org_scraper -- scrape en.wikinews.org
# 20121218 Paul Huygen
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

INDEX_URL = "http://en.wikinews.org/wiki/Category:Public_domain_articles"
BASE_URL = "http://en.wikinews.org" 

import logging
log = logging.getLogger(__name__)

from amcat.scraping.scraper import HTTPScraper
from amcat.scraping.document import HTMLDocument
from amcat.tools import toolkit
from amcat.scraping.toolkit import todate
from urlparse import urljoin

class WikiNewsScraper(HTTPScraper):
    medium_name = "wikinews"

    def url_of_next_indexpage_or_empty_string(self, oldurl):
       for ael in self.getdoc(oldurl).cssselect('a[title="Category:Public domain articles"]'):
         href = ael.get('href')
         if(href.find('pagefrom') > 0) :
           return urljoin(BASE_URL, href)
       return ""

    def yield_docs_pointed_to_by_a_elements_in_list_elements_in_mw_pages_section(self, url):
       for div in self.getdoc(url).cssselect('#mw-pages'):
          for li in div.cssselect('ul li'):
              if  li.cssselect('a'):
                 href = li.cssselect('a')[0].get('href')
                 href = urljoin(BASE_URL, href)
                 yield HTMLDocument(url=href)

    def _get_units(self):
         url = INDEX_URL
         while url :
           for doc in self.yield_docs_pointed_to_by_a_elements_in_list_elements_in_mw_pages_section(url):
             yield doc
           url = self.url_of_next_indexpage_or_empty_string(url)

    def date_of_unit(self, doc):
         # find element like '<span id="publishDate" class="value-title" title="2004-11-15">'
         # and extract "title".
         return doc.cssselect('#publishDate')[0].get('title')

    def _scrape_unit(self, doc):
        doc.doc = self.getdoc(doc.props.url)
        doc.props.headline = doc.doc.cssselect('h1.firstHeading')[0].text_content()
        doc.props.text = doc.doc.cssselect('#mw-content-text')[0]
        doc.props.date = toolkit.readDate(self.date_of_unit(doc.doc)).date()
        yield doc

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WikiNewsScraper)
