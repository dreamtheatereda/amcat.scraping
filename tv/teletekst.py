#!/usr/bin/python
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
from amcat.scraping.scraper import HTTPScraper
from amcat.scraping.document import HTMLDocument
from amcat.tools.toolkit import readDate

class TeletekstScraper(HTTPScraper):
    medium_name = "Teletekst"
    def _get_units(self):
        self.open("http://nos.nl/")
        self.open("http://cookies.publiekeomroep.nl/accept/")
        for item in self.getdoc("http://feeds.nos.nl/nosnieuws").cssselect("item"):
            yield HTMLDocument(url = item.cssselect("link")[0].tail, date = readDate(item.cssselect('pubDate')[0].text))

    def _scrape_unit(self, article):
        article.prepare(self)
        article.props.text = article.doc.cssselect("#article-content p")
        article.props.headline = article.doc.cssselect("#article h1")[0].text_content().strip()
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(TeletekstScraper)

