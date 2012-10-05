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
from urllib2 import HTTPError

INDEX_URL = "http://www.nrc.nl/{}/"

from amcat.scraping.scraper import HTTPScraper,DatedScraper

class WeblogNRCScraper(HTTPScraper, DatedScraper):
    medium_name = "NRC website - blogs"
    t = "weblogs"

    def __init__(self, *args, **kwargs):
        super(WeblogNRCScraper, self).__init__(*args, **kwargs)

    def _get_units(self):

        url = INDEX_URL.format(self.t)
        index = self.getdoc(url) 
        
        for unit in index.cssselect('div.voorjekijkendoorlopen h2'):
            href = unit.cssselect('a')[0].get('href').lstrip("/.")
            url = urljoin("http://www.nrc.nl/",href)
            y = self.options['date'].year
            m = self.options['date'].month

            link = urljoin(url,"{y:04d}/{m:02d}/".format(**locals()))
            try:
                self.open(link)
            except HTTPError: #not up to date
                continue
            yield IndexDocument(url=link, date=self.options['date'])
            

    def _scrape_unit(self, ipage): 

        ipage.prepare(self)
        ipage.bytes = ""
        ipage.doc = self.getdoc(ipage.props.url)
        ipage.page = ""
        ipage.props.category = ipage.doc.cssselect("li.jebenthier a")[0].text

        for dd in ipage.doc.cssselect("div.lijstje dd"):
            _date = "-".join(dd.cssselect("a")[0].get('href').split("/")[4:7])
            date = readDate(_date)
            if date.date() < self.options['date']:
                break
            elif date.date() == self.options['date']:
                href = dd.cssselect("a")[0].get('href').lstrip("./")
                url = urljoin("http://www.nrc.nl/",href)
                page = HTMLDocument(date = ipage.props.date,url=url)
                page.prepare(self)
                page.doc = self.getdoc(page.props.url)
                yield self.get_article(page)

                ipage.addchild(page)

        yield ipage

    def get_article(self, page):
        try:
            page.props.author = page.doc.cssselect("div.author a")[0].text
        except IndexError:
            page.props.author = "unknown"
        page.props.headline = page.doc.cssselect("div.article h1")[0]
        page.props.text = page.doc.cssselect("#broodtekst")[0].text_content()
        page.coords = ""
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WeblogNRCScraper)


