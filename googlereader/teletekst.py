# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
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

from amcat.scraping.scrapers.googlereader import GoogleReaderScraper
from amcat.scraping.document import HTMLDocument
from datetime import datetime

class TeletekstScraper(GoogleReaderScraper):
    feedname = "NOS Teletekst"

    def _scrape_unit(self, item):
        article = HTMLDocument(
            headline = item['title'],
            date = datetime.fromtimestamp(item['published']),
            url = item['canonical'][0]['href']
            )
        article.prepare(self)
        article.props.text = article.doc.cssselect("#article-content p")
        yield article

if __name__ == "__main__":
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping.controller")
    amcatlogging.info_module("amcat.scraping.scraper")
    cli.run_cli(TeletekstScraper)
