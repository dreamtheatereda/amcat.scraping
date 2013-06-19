#!/usr/bin/python
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
from amcat.scraping.document import HTMLDocument
from urlparse import urljoin
from datetime import date, datetime
import logging; log = logging.getLogger(__name__)



class TeletekstScraper(HTTPScraper, DatedScraper):
    medium_name = "Teletekst"
    base_url = "http://teletekst.mobile.nob.nl/xda-teletekst/index.jsp"
    page_url = "http://teletekst.mobile.nob.nl/xda-teletekst/index.jsp?page=TTARTICLE_PAGE_{page:03d}_{tab:02d}.htm"

    def _get_units(self):
        self.index_urls = [self.page_url.format(page=101, tab=1)]
        p101 = self.getdoc(self.index_urls[0])
        for a in p101.cssselect("p a"):
            href = a.get('href')
            url = urljoin(self.base_url, href)
            self.index_urls.append(url)
        for u in self.index_urls:
            for a in self.getdoc(u).cssselect("a"):
                yield a
        
    def _scrape_unit(self, a):
        url = urljoin(self.base_url, a.get('href'))
        if url not in self.index_urls and len(a.text) == 3:
            page = HTMLDocument(date = date.today(), url = url)
            page.props.time_scraped = datetime.now()
            page.props.pagenr = int(a.text)
            page.prepare(self)
            try:
                article = self.get_article(page)
            except ValueError:
                log.exception("get_article failed")
            else:
                yield article

    def get_article(self, page):
        nextpage = False
        for tag in page.doc.cssselect("table, img"):
            if tag.get('alt') == "volgende":
                nextpage = True
            tag.drop_tree()
        title = page.doc.cssselect("title")[0].text
        if title == "Teletekst pagina niet beschikbaar":
            raise ValueError(title)
        page.props.headline = title.split(":")[1]
        page.props.text = page.doc.cssselect("body")
        if nextpage:
            page.props.text += self.add_text(page.props.pagenr, 2)
        return page

    def add_text(self, page, tab):
        url = self.page_url.format(**locals())
        doc = self.getdoc(url)
        if self.nextpage(doc):
            text = self.add_text(page = page, tab = tab + 1)    
        else:
            text = []
        return doc.cssselect("body") + text

    def nextpage(self, doc):
        more = False
        for tag in doc.cssselect("table, img"):
            if tag.get('alt') == "volgende":
                more = True
            tag.drop_tree()
        return more
            

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(TeletekstScraper)

