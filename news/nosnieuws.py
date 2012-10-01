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

from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, IndexDocument

from urlparse import urljoin

INDEX_URL = "http://www.nos.nl/"
URLS = ["http://www.nos.nl/nieuws/","http://www.nos.nl/sport/"]

class NOSNieuwsScraper(HTTPScraper, DBScraper):
    medium_name = "NOS nieuws"

    def __init__(self, *args, **kwargs):
        super(NOSNieuwsScraper, self).__init__(*args, **kwargs)
        
            
        
        
    def _get_units(self):
        """get pages"""
        
        year = str(self.options['date'].year)
        month = str(self.options['date'].month)
        day = str(self.options['date'].day)
        if len(month) == 1:
            month = "0"+month
        if len(day) == 1:
            day = "0"+day
        for url in URLS:
            href = url
            index_1 = self.getdoc(url)
            cats = index_1.cssselect("ul.sub li")
            for cat in cats:
                link = cat.cssselect("a")[0].get('href')
                url = urljoin(url,link)
                add = "archief/datum/{year}-{month}-{day}".format(year=year,month=month,day=day)
                url = urljoin(url,add)
                category = cat.cssselect("a span")[0].text
                yield IndexDocument(url=url,date = self.options['date'],category = category)

        
    def _scrape_unit(self, ipage):
        """gets articles from a page"""
        ipage.prepare(self)
        ipage.page = ""
        ipage.doc = self.getdoc(ipage.props.url)
        
        for li in ipage.doc.cssselect("div#article ul.news-list li"):
            url = li.cssselect("a")[0].get('href')
            url = urljoin(INDEX_URL,url)
            page = HTMLDocument(date = self.options['date'],url=url)
            page.prepare(self)
            page.doc = self.getdoc(page.props.url)
            page.coords = ""

            try: #some pages are custom, with a different layout
                yield self.get_article(page) 
                ipage.addchild(page)
            except IndexError: #cssselect() will fail first, raising an index error
                pass #these pages are often temporarily

            

        yield ipage

    def get_article(self, page):
        page.props.headline = page.doc.cssselect("div#article h1")[0]
        content = page.doc.cssselect("div#article-content")[0]
        content.cssselect("a#btn-share")[0].drop_tree()
        page.props.text = content.text_content()
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(NOSNieuwsScraper)
