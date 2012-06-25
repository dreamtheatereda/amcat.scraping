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

INDEX_URL = "http://teletekst.mobile.nob.nl/xda-teletekst/index.jsp?page=TTARTICLE_PAGE_{page}_{tab}.htm"
BASE_URL = "http://teletekst.mobile.nob.nl/xda-teletekst/index.jsp"

class TeletekstScraper(HTTPScraper, DBScraper):
    medium_name = "Teletekst"

    def __init__(self, *args, **kwargs):
        super(TeletekstScraper, self).__init__(*args, **kwargs)

    def _get_units(self):
        index = [INDEX_URL.format(page=101,tab="01")]
        index_1 = self.getdoc(index[0])
        for a in index_1.cssselect("p a"):
            href = a.get('href')
            url = urljoin(BASE_URL,href)
            index.append(url)
        for ind in index:
            yield IndexDocument(url=ind,date=self.options['date'])        



        
    def _scrape_unit(self, ipage):
        """gets articles from an index page"""
        ipage.prepare(self)
        ipage.bytes = ""
        ipage.doc = self.getdoc(ipage.props.url)
        ipage.page = ipage.props.url.split("_")[2]
        ipage.doc.cssselect("p")[0].drop_tree()
        for a in ipage.doc.cssselect("a"):
            href = a.get('href')
            url = urljoin(BASE_URL,href)
            page = HTMLDocument(date = ipage.props.date,url=url)
            page.prepare(self)
            page.doc = self.getdoc(page.props.url)
            yield self.get_article(page)

            ipage.addchild(page)

        yield ipage

    def get_article(self, page):
        page.props.author = ""
        page.props.headline = ""
        for table in page.doc.cssselect("table"):
            table.drop_tree()
        headlinedoc = page.doc
        textdoc = page.doc
        for p in headlinedoc.cssselect("p"):
            p.drop_tree()
        
        headline_text = headlinedoc.text_content().split("\n")[0].split(":")[1:]
        headline_text = ":".join(headline_text) 
        page.props.text = textdoc.text_content()
        page.coords = ""
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TeletekstScraper)

