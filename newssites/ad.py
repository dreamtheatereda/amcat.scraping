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
from lxml import etree

INDEX_URL = "http://www.ad.nl/ad/nl/1401/archief/integration/nmc/frameset/archive/archiveDay.dhtml?archiveDay={y:04d}{m:02d}{d:02d}"


from amcat.scraping.scraper import HTTPScraper,DatedScraper

class WebADScraper(HTTPScraper, DatedScraper):
    medium_name = "AD website"

    def __init__(self, *args, **kwargs):
        super(WebADScraper, self).__init__(*args, **kwargs)


    def _get_units(self):
        

        y = self.options['date'].year
        m = self.options['date'].month
        d = self.options['date'].day
        

        url = INDEX_URL.format(**locals())
        index = self.getdoc(url) 
        
        for unit in index.cssselect('dl dd'):
            href = unit.cssselect('a')[0].get('href')
            yield HTMLDocument(url=href, date=self.options['date'])
        
    def _scrape_unit(self, page): 
        
        page.prepare(self)
        page.doc = self.getdoc(page.props.url)
        yield self.get_article(page)
        

    def get_article(self, page):
        page.props.author = etree.tostring(page.doc.cssselect("span.author")[0]).split("<br>")[0].split(":")[1].strip()
        page.props.headline = page.doc.cssselect("#articleDetailTitle")[0].text
        page.props.text = page.doc.cssselect("section#detail_content")[0].text_content() #yay for html5
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WebADScraper)


