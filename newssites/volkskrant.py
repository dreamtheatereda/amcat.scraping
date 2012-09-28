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

from amcat.scraping.document import Document, HTMLDocument, IndexDocument

from urlparse import urljoin
from amcat.tools.toolkit import readDate
from datetime import datetime

INDEX_URL = "http://www.volkskrant.nl/vk/article/pagedListContent.do?language=nl&navigationItemId=2&navigation=&useTeaserType=2&page={}"


from amcat.scraping.scraper import HTTPScraper,DatedScraper

class WebVolkskrantScraper(HTTPScraper, DatedScraper):
    medium_name = "Volkskrant website"

    def __init__(self, *args, **kwargs):
        super(WebVolkskrantScraper, self).__init__(*args, **kwargs)

    def _get_units(self):
        i = 0
        index = self.getdoc(INDEX_URL.format(i)) 
        date = datetime.now() #date will be the date of the last article iterated over.
        while date.date() >= self.options['date']:
            for unit in index.cssselect('ul.list_node'):
                href = unit.cssselect('a')[0].get('href')
                href = urljoin("http://www.volkskrant.nl",href)
                article = HTMLDocument(url=href)
                article.doc = self.getdoc(article.props.url)
                date = readDate(article.doc.cssselect("div.time_post")[0].text_content())
                if date.date() == self.options['date']:
                    article.date = date.date()
                    yield article
                elif date.date() < self.options['date']:
                    break

                
            i +=1
            index = self.getdoc(INDEX_URL.format(i))

        
    def _scrape_unit(self, page): 

        page.prepare(self)
        yield self.get_article(page)

    def get_article(self, page):
        try:
            author = page.doc.cssselect("span.author")[0]
            if "OPINIE" in author.text:
                page.props.author = author.text.split("-")[1].strip()
            elif "Door:" in author.text:
                page.props.author = author.text.split("Door:")[1].strip()
            else:
                page.props.author = author.text
        except IndexError:
            time_post = page.doc.cssselect("div.time_post")[0].text
            if "bron" in time_post:
                page.props.author = page.doc.cssselect("div.time_post")[0].text.split("bron:")[1]
            else:
                page.props.author = "None"
        
        page.props.headline = page.doc.cssselect("#articleDetailTitle")[0].text
        page.props.text = page.doc.cssselect("#art_box2")[0].text_content()
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WebVolkskrantScraper)
