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

from amcat.scraping.document import Document, HTMLDocument

from urlparse import urljoin
from amcat.tools.toolkit import readDate

BASE_URL = "http://www.powned.tv"
START_URL = "http://www.powned.tv/nieuws/binnenland/"

from amcat.scraping.scraper import HTTPScraper,DatedScraper

class PownewsScraper(HTTPScraper, DatedScraper):
    medium_name = "nieuwssite powned"

    def __init__(self, *args, **kwargs):
        super(PownewsScraper, self).__init__(*args, **kwargs)
        self.open(BASE_URL)
        self.open("http://cookies.publiekeomroep.nl/accept/")

    def _get_units(self):

        start = self.getdoc(START_URL) 
        new_url = urljoin(BASE_URL, start.cssselect("a.buttonarrow")[0].get('href'))
        page = self.getdoc(new_url)
        year = " "+new_url.split("/")[4]
                
        date = readDate(page.cssselect('ul.articlelist li span.t')[0].text[:-5] + year).date()
        while date >= self.options['date']:
            year = " "+new_url.split("/")[4]
 
            for unit in page.cssselect('ul.articlelist li'):
                date = readDate(unit.cssselect("span.t")[0].text[:-5] +year).date()
                if str(self.options['date']) in str(date):
                    href = unit.cssselect('a')[0].get('href')
                    yield HTMLDocument(url=href, date=self.options['date'])
            new_url = page.cssselect("#maincol-large div a.left")[0].get('href')
            page = self.getdoc(new_url)





        
    def _scrape_unit(self, page): 
       
        page.prepare(self)
        page.doc = self.getdoc(page.props.url)
        for comment in self.get_comments(page):
            yield comment
        yield self.get_article(page)


    def get_article(self, page):
        page.props.author = page.doc.cssselect("#artikel-footer .author-date")[0].text.split("|")[0].strip()
        page.props.headline = page.doc.cssselect("div.acarhead h1")[0].text
        page.props.text = [page.doc.cssselect("div.artikel-intro")[0], page.doc.cssselect("div.artikel-main")[0]]
        return page

    def get_comments(self,page):
        for div in page.doc.cssselect("#comments div.comment"):
            comment = Document(parent=page)
            comment.props.text = div.cssselect("p")[0]
            footer = div.cssselect("p.footer")[0].text_content().split(" | ")
            comment.props.author = footer[0].strip()
            comment.props.date = readDate(footer[1].strip())
            yield comment
                                         




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(PownewsScraper)


