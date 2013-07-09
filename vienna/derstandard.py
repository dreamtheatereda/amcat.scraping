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

from amcat.scraping.document import HTMLDocument
from amcat.tools.toolkit import readDate
from amcat.scraping.scraper import HTTPScraper, DatedScraper

class DerStandardScraper(HTTPScraper, DatedScraper):
    medium_name = "derstandard.at"
    index_url = "http://derstandard.at/Archiv/{self.options[date].year}/{self.options[date].month}/{self.options[date].day}"

    def _get_units(self):
        index_url = self.index_url.format(**locals())
        doc = self.getdoc(index_url)
        for li in doc.cssselect("#content ul.chronologie li"):
            article = HTMLDocument(
                date = readDate(li.cssselect("div.date")[0].text_content()),
                headline = li.cssselect("h3")[0].text_content().strip(),
                url = urljoin(index_url, li.cssselect("h3 a")[0].get('href'))
                )
            kicker = li.cssselect("div.text h6 a")
            article.props.kicker = kicker and kicker[0].text or None
            yield article
        
    def _scrape_unit(self, article):
        article.prepare(self)
        article.props.section = " > ".join([span.text_content() for span in article.doc.cssselect("#breadcrumb span.item")[1:]])
        article.props.text = article.doc.cssselect("#artikelBody div.copytext")[0]
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(DerStandardScraper)


