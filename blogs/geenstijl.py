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


INDEX_URL = "http://www.geenstijl.nl/"

class GeenstijlScraper(HTTPScraper, DBScraper):
    medium_name = "geenstijl.nl"

    def __init__(self, *args, **kwargs):
        super(GeenstijlScraper, self).__init__(*args, **kwargs)


   

    def _get_units(self):
        #only works for current day
        yield IndexDocument(url=INDEX_URL,date=self.options['date'])
    
    def _scrape_unit(self, ipage):
        ipage.prepare(self)
        ipage.doc = self.getdoc(ipage.props.url)
        ipage.page = self.getdoc(INDEX_URL)
        units = ipage.doc.cssselect('article.artikel')
        correct_date = str(self.options['date']).split("-")
        correct_date = correct_date[2]+"-"+correct_date[1]+"-"+correct_date[0].lstrip("20")
        for article_unit in units:
            date = article_unit.cssselect("footer time")[0].text.split("|")[0].rstrip(" ")
            if correct_date in date:
                href = article_unit.cssselect("footer a")[0].get('href')
                page = HTMLDocument(url=href, date=self.options['date'])
                page.prepare(self)
                page.doc = self.getdoc(href)
                page = self.get_article(page)
                yield page
                ipage.addchild(page)

        yield ipage
        

    def get_article(self, page):
        page.props.author = page.doc.cssselect("article.artikel footer")[0].text.split("|")[0]
        page.props.headline = page.doc.cssselect("article.artikel h1")[0].text
        page.props.text = page.doc.cssselect("article.artikel p")[0].text_content()
        page.coords = ""
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(GeenstijlScraper)
