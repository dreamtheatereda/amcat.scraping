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

from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.scraping.document import HTMLDocument

from amcat.tools import toolkit
#from amcat.model.medium import Medium

from urlparse import urljoin
import datetime


class ParoolScraper(HTTPScraper, DatedScraper):
    medium_name = 'Parool'
    index_url = "http://m.parool.nl/24-uur-nieuws.html"
        
    def _get_units(self):
        date = self.options['date']
        if date == datetime.date.today()-datetime.timedelta(days=1):
            for li in self.getdoc(self.index_url).cssselect('#cntr4 li.clearfix'):
                if "gisteren" in li.cssselect("p.commentsBox")[0].text:
                    href = li.cssselect('a')[0].get('href')
                    href = urljoin("http://m.parool.nl/", href)
                    yield HTMLDocument(url=href)
        elif date == datetime.date.today():
            for li in self.getdoc(self.index_url).cssselect('ul.cntr4 li.clearfix'):
                if "gisteren" not in li.cssselect("p.commentsBox"):
                    href = li.cssselect('a')[0].get('href')
                    href = urljoin("m.parool.nl", href)
                    yield HTMLDocument(url=href)
        else:
            print( '\nblaat.\n' )

    def _scrape_unit(self,doc):
        doc.doc = self.getdoc(doc.props.url)
        doc.props.headline = doc.doc.cssselect('h1.fontXL')[0].text
        doc.props.byline = doc.doc.cssselect('p.article')[0].text
        doc.props.text = "\n".join([p.text_content() for p in doc.doc.cssselect("#mainCntr p")])
        yield doc


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(ParoolScraper)
