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

INDEX_URL = "http://www.spitsnieuws.nl/archives/%(year)s%(month)02d/"

import logging
log = logging.getLogger(__name__)

from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument
from amcat.tools import toolkit
from amcat.scraping.toolkit import todate
from urlparse import urljoin

class SpitsnieuwsScraper(DatedScraper, HTTPScraper):

    def get_units(self):
        date = self.options['date']
        url = INDEX_URL % dict(year=date.year, month=date.month)
        
        for li in self.getdoc(url).cssselect('.ltMainContainer ul li.views-row'):
            docdate = toolkit.readDate(li.text.strip('\n\r \u2022:')).date()
            if docdate == todate(date):
                href = li.cssselect('a')[0].get('href')
                href = urljoin(INDEX_URL, href)

                yield HTMLDocument(url=href)

    def scrape_unit(self, doc):
        doc.doc = self.getdoc(doc.props.url)
        doc.props.headline = doc.doc.cssselect('h2.title')[0].text
        doc.props.text = doc.doc.cssselect('div.main-article-container > p')

        footer = doc.doc.cssselect('.article-options > div')[0].text.split('|')
        doc.props.author = footer[0].strip()
        doc.props.date = toolkit.readDate(" ".join(footer[1:3]))

        yield doc

    def comments(self, doc):
        log.info(doc.parent)

        divs = doc.doc.cssselect('#comments .reactiesList')

        for div in divs:
            comm = doc.copy()

            comm.props.text = div.cssselect('p')[0]
            comm.props.author = div.cssselect('strong')[0].text

            dt = [t.strip() for t in div.itertext() if t.strip()][-3]
            comm.props.date = toolkit.toDate(dt)

            yield comm

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping.scraper")
    amcatlogging.info_module("amcat.scraping.document")
    cli.run_cli(SpitsnieuwsScraper)
