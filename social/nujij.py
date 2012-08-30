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

from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import IndexDocument, HTMLDocument, Document

#from urllib import urlencode
from urlparse import urljoin
from amcat.tools.toolkit import readDate
from datetime import timedelta
from datetime import date

from lxml import etree
INDEX_URL = "http://www.nujij.nl/"

class NuJijScraper(HTTPScraper, DatedScraper):
    medium_name = "Nujij.nl"

    def __init__(self, *args, **kwargs):
        super(NuJijScraper, self).__init__(*args, **kwargs)


        
    def _get_units(self):
        index = self.getdoc(INDEX_URL)
        for category in index.cssselect("dl.topmenu dd a")[1:]:
            url = category.get('href')
            for doc in self.get_articles(self.getdoc(url)):
                yield doc
            nxt = self.getdoc(url)        
            while len(nxt.cssselect("div.pages a.next"))==1:
                nxt_url = urljoin(url,nxt.cssselect("div.pages a.next")[0].get('href'))
                print("\n"+nxt_url+"\n")
                nxt = self.getdoc(nxt_url)
                for doc in self.get_articles(nxt):
                    yield doc
            
    def get_articles(self,page):
        for article in page.cssselect("div.columnLeft div.bericht"):
            _datum = article.cssselect("span.tijdsverschil")[0].get('publicationdate')
            datum = readDate(_datum)
            print("checking date for {url}".format(url=article.cssselect("h3.title a")[0].get('href')))
            print("Scraped date: {sdate}. Article date: {adate}. Correct? -> {correct}".format(sdate=self.options['date'],adate=_datum,correct=(self.options['date'].__str__() in datum.__str__())))
            if self.options['date'].__str__() in datum.__str__():
                href = article.cssselect("h3.title a")[0].get('href')+"?pageStart=1"
                yield HTMLDocument(url=href)
            elif self.options['date']>datum:
                break

    def _scrape_unit(self, page):
        try:
            page.prepare(self)
        except UnicodeEncodeError:
            pass
        else:
            page.doc = self.getdoc(page.props.url)
            page.props.section = page.doc.cssselect("div.article-header div.tabbar h2.title")[0].text
            page.props.author = page.doc.cssselect("div.bericht-details")[0].text_content().split("door")[1].strip()
            page.props.headline = page.doc.cssselect("div.articleheader h1.title")[0].text_content().strip()
            page.props.text = page.doc.cssselect("div.articlecontent div.articlebody")[0].text.strip()
            page.props.link = page.doc.cssselect("div.bericht-link")[0].get('href')
            try:
                page.props.tags = page.doc.cssselect("span.bericht-tags-links")[0].text_content().rstrip(".")
            except IndexError:
                pass
            
            for comment in self.scrape_comments(page):
                yield comment
            
        yield page

    def scrape_comments(self,page):
        nxt = page.doc
        if len(nxt.cssselect("div.pages a.next")) >= 1:
            while len(nxt.cssselect("div.pages a.next")) >= 1:
                try:
                    nxt = self.getdoc(nxt.cssselect("div.pages a.next")[0].get('href'))
                except ValueError:
                    nxt = self.getdoc(urljoin(INDEX_URL,nxt.cssselect("div.pages a.next")[0].get('href')))
                for li in nxt.cssselect("ol.reacties li.hidenum"):
                    comment = Document(parent=page)
                    if not("<b>Reageer als eerste op dit bericht</b>" in etree.tostring(li) or "gebruiker verwijderd" in etree.tostring(li)):
                        try:
                            comment.props.text = li.cssselect("div.reactie-body")[0].text.strip()
                            comment.props.author = li.cssselect("strong")[0].text
                            comment.props.date = readDate(li.cssselect("span.tijdsverschil")[0].get('publicationdate'))
                            yield comment
                        except IndexError:
                            pass
        else:
            for li in nxt.cssselect("ol.reacties li.hidenum"):
                comment = Document(parent=page)
                if not "<b>Reageer als eerste op dit bericht</b>" in etree.tostring(li):
                    comment.props.text = li.cssselect("div.reactie-body")[0].text.strip()
                    comment.props.author = li.cssselect("strong")[0].text
                    comment.props.date = readDate(li.cssselect("span.tijdsverschil")[0].get('publicationdate'))
                    yield comment


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(NuJijScraper)


