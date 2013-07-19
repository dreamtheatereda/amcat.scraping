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

from urlparse import urljoin
import re

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate

class GMXScraper(HTTPScraper, DatedScraper):
    medium_name = "gmx.at"
    index_url = "http://www.gmx.at/themen/all/{d.year}/{d.month}/{d.day}/"

    def _get_units(self):
        d = self.options['date']
        index = self.getdoc(self.index_url.format(**locals()))
        for div in index.cssselect("#main div.unit"):
            yield HTMLDocument(url = div.cssselect("a")[0].get('href'))

    def _scrape_unit(self, article):
        article.prepare(self)
        article.props.date = readDate(article.doc.cssselect("#datetime")[0].text_content())
        article.props.section = " > ".join(article.props.url.split("/")[4:-1])
        article.props.headline = article.doc.cssselect("#headline")[0].text_content().strip()
        article.props.text = article.doc.cssselect("#teaser") + article.doc.cssselect("#main > p")
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(GMXScraper)



