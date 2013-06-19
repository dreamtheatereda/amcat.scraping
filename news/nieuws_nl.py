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
import json
from datetime import date, datetime
from lxml import html

class Nieuws_nlScraper(HTTPScraper, DatedScraper):
    medium_name = "Nieuws.nl"
    index_url = "https://www.nieuws.nl"

    def _get_units(self):
        index_page = self.getdoc(self.index_url)
        for category_url in [a.get('href') for a in index_page.cssselect("#mainMenu a.menuMainItem")]:
            for a, _date in self.get_articles(category_url):
                article = HTMLDocument(date = _date)
                article.props.url = a.get('href')
                article.props.section = article.props.url.split("/")[3]
                h3 = a.cssselect("h3")
                if h3:
                    article.props.headline = h3[0].text_content()
                elif a.get('title'):
                    article.props.headline = a.get('title')
                if a.cssselect("div.text p"):
                    article.props.thumbnail = a.cssselect("div.text p")
                yield article
                    
    page_url = "{category_url}?ajax=1&after={data_after}&ajax=1"
    def get_articles(self, category_url):
        page_doc = self.getdoc(category_url)
        data_after = page_doc.cssselect("#nextPage")
        if not data_after:
            for a, _date in self.scrape_page(page_doc):
                if _date.date() == self.options['date']:
                    yield a, _date
                elif _date.date() < self.options['date']:
                    break
        else:
            data_after = data_after[0].get('data-after')
            while True:
                br = False
                for a, _date in self.scrape_page(page_doc):
                    if _date.date() == self.options['date']:
                        yield a, _date
                    elif _date.date() < self.options['date']:
                        br = True
                        break
                if br:
                    break
                data_after = page_doc.cssselect("#nextPage")[0].get('data-after')
                page_doc = json.loads(self.open(self.page_url.format(**locals())).read())
                page_doc = html.fromstring(page_doc['content']['div#nextPage'])

    def scrape_page(self, page_doc):
        for a in page_doc.cssselect("a.article"):
            date_str = a.cssselect("div.meta span.time")[0].text.strip()
            if len(date_str) == 5:
                if ":" in date_str:
                    today = date.today()
                    hour, minute = [int(n) for n in date_str.split(":")]
                    self._date = datetime(today.year, today.month, today.day, hour, minute)
                elif "-" in date_str:
                    day, month = [int(n) for n in date_str.split("-")]
                    if hasattr(self, '_date'):
                        self._date = datetime(self._date.year, month, day)
                    else:
                        self._date = datetime(date.today().year, month, day)
            else:
                if "Gepubliceerd" in date_str:
                    self._date = readDate(date_str.split(":")[1])
                else:
                    self._date = readDate(date_str)
            yield a, self._date

    def _scrape_unit(self, article): 
        article.prepare(self)
        article.props.last_updated = readDate(article.doc.cssselect("div.meta span.time")[0].text.split(":")[1])
        article.props.intro = article.doc.cssselect("div.intro h2")
        article.props.text = article.doc.cssselect("div.article div.text")[0]
        try:
            article.props.author = article.doc.cssselect("div.metafooter span.author")[0].text.split(":")[1].strip()
        except IndexError:
            pass
        yield article
        
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Nieuws_nlScraper)


