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

INDEX_URL = "http://www.depers.nl/"

from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument

from urlparse import urljoin

class DePersScraper(HTTPScraper, DatedScraper):
    """ Scrape the news from depers.nl."""
    medium_name = "De Pers - news"

    def get_categories(self):
        """ Yields the urls to all the pages contianing the categories.
        """
        doc = self.getdoc(INDEX_URL)
        for link in doc.cssselect("div.subtabs ul li a"):
            yield urljoin(INDEX_URL, link.get("href"))

    def _get_units(self):
        for url in self.get_categories():
            day_url = urljoin(url, "%04d%02d%02d.html" % (
                self.options['date'].year,
                self.options['date'].month,
                self.options['date'].day
            ))

            if not day_url.startswith(INDEX_URL): continue

            doc = self.getdoc(day_url)
            for article in doc.cssselect("div.lbox500 h2 a"):
                url = urljoin(day_url, article.get("href"))

                if '/video/' in url: continue

                yield HTMLDocument(
                    url = urljoin(day_url, article.get("href")),
                    headline = article.text,
                    date = self.options['date']
                )

    def _scrape_unit(self, doc):
        doc.prepare(self)
        if doc.doc.cssselect("div.lbox440"):
            doc.props.text = doc.doc.cssselect("div.lbox440")[0].cssselect('p')
        else:
            doc.props.text = ""
        yield doc

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(DePersScraper)
