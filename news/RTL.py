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

#this piece makes it possible to quickly create a new scraper. As there are thousands of papers and other mediums out on the web, we can never have enough scrapers.

from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, IndexDocument
from amcat.scraping import toolkit as stoolkit #remove this line if not used

#possibly useful imports:

#from urllib import urlencode
#from urlparse import urljoin

BASE_URL = "http://www.rtl.nl/"
INDEX_URL = "http://www.rtl.nl/actueel/rtlnieuws/"

class RTLScraper(HTTPScraper, DBScraper):
    medium_name = "RTL Nieuws"

    def __init__(self, *args, **kwargs):
        
        super(RTLScraper, self).__init__(*args, **kwargs)




    def _get_units(self):

        index_dict = {
            'year' : self.options['date'].year,
            'month' : self.options['date'].month,
            'day' : self.options['date'].day
        }


        index = self.getdoc(INDEX_URL) 

        units = index.cssselect('div#main_navigation div.nav_item')
        for article_unit in units[1:6]: #home - opmerkelijk
            href = article_unit.cssselect('a')[0].get('href')
            url = urljoin(BASE_URL,href)
            yield IndexDocument(url=url, date=self.options['date'])






        
    def _scrape_unit(self, ipage): # 'ipage' means index_page
        """gets articles from an index page"""
        ipage.prepare(self)
        ipage.bytes = "?" #whats this?


        ipage.doc = self.getdoc(ipage.props.url)
        ipage.page = ""
        ipage.props.category = ipage.doc.cssselect("div.category_lead_container h2").text
        articlelinks = []
        for a in ipage.doc.cssselect("div.category_lead_container h3 a"):
            articlelinks.append(a.get('href'))
        for a in ipage.doc.cssselect("ul#archive_container_vandaag li a"):
            articlelinks.append(a.get('href'))

        for a in articlelinks:
            
            url = urljoin(BASE_URL,a)
            page = HTMLDocument(date = ipage.props.date,url=url)
            page.prepare(self)
            page.doc = self.getdoc(page.props.url)
            yield self.get_article(page)

            ipage.addchild(page)

        yield ipage

    def get_article(self, page):
        page.props.author = page.doc.cssselect("div.fullarticle_tagline")[0].text.split("|")[0]
        page.props.headline = page.doc.cssselect("h1.title")[0].text
        page.props.text = page.doc.cssselect("article")[0].text_content()
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(RTLScraper)

