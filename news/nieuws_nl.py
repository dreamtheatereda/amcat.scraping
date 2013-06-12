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

from amcat.scraping.document import HTMLDocument
from amcat.tools.toolkit import readDate
from amcat.scraping.scraper import HTTPScraper,DatedScraper

class Nieuws_nlScraper(HTTPScraper, DatedScraper):
    medium_name = "nieuws.nl"
    index_url = "https://www.nieuws.nl"

    def _get_units(self):
        index_page = self.getdoc(self.index_url)
        for category_url in [a.get('href') for a in index_page.cssselect("#mainMenu a.menuMainItem")]:
            for a, _date in self.get_articles(category_url):
                article = HTMLDocument(date = _date)
                article.props.url = a.get('href')
                article.props.section = a.cssselect("div.meta span.tag")[0].text
                article.props.headline = a.cssselect("h3")[0].text_content()
                article.props.thumbnail = a.cssselect("div.text p")
                yield article
                    
    page_url = "{category_url}?ajax=1&after={data_after}&ajax=1"
    def get_articles(self, category_url):
        cat_doc = self.getdoc(category_url)
        data_after = cat_doc.cssselect("#nextPage")
        if not data_after:
            for a in cat_doc.cssselect("a.article"):
                _date = readDate(a.cssselect("div.meta span.time")[0].text.split(":")[1])
                if _date.date() == self.options['date']:
                    yield a, _date
            return
        else:
            data_after = data_after[0].get('data-after')
        while True:
            page_doc = self.getdoc(self.page_url.format(**locals()))
            for a in page_doc.cssselect("a.article"):
                _date = readDate(a.cssselect("div.meta span.time")[0].text.split(":")[1])
                if _date.date() == self.options['date']:
                    yield a, _date
                elif _date.date() < self.options['date']:
                    return
            data_after = cat_doc.cssselect("#nextPage").get('data-after')
            
    def _scrape_unit(self, article): 
        article.prepare(self)
        article.props.last_updated = readDate(article.doc.cssselect("div.meta span.time")[0].text.split(":")[1])
        article.props.intro = article.doc.cssselect("div.intro h2")
        article.props.text = article.doc.cssselect("div.article div.text")[0]
        article.props.author = article.doc.cssselect("div.metafooter span.author")[0].text.split(":")[1].strip()
        yield article
        
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Nieuws_nlScraper)


