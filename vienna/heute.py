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
from urllib2 import HTTPError

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate

class HeuteScraper(HTTPScraper, DatedScraper):
    medium_name = "heute.at"
    initial_url = "http://heute.at"
    index_url = "http://heute.at/datum.={d.day:02d}-{d.month:02d}-{d.year:02d}/"

    def _get_units(self):
        self.open(self.initial_url)
        d = self.options['date']
        index_url = self.index_url.format(**locals())
        for div in self.getdoc(index_url).cssselect("div.contentContainer div.listItem"):
            a = div.cssselect("h2 a")[0]
            
            yield HTMLDocument(
                url = urljoin(index_url, a.get('href')),
                headline = a.text_content().strip(),
                )

    def _scrape_unit(self, article):
        article.prepare(self)
        article.props.section = " > ".join(article.props.url.split("/")[3:-1])
        article.props.date = readDate(article.doc.cssselect("#detailContentBlock p.Right")[0].text_content())
        if article.props.date.date() != self.options['date']:
            print('Faulty date')
            return
        externalid = article.props.url.split("/")[-1].lstrip("art").split(",")
        article.props.externalid = int(externalid[0])
        article.props.externalid_2 = int(externalid[1])
        article.doc.cssselect("div.textRight")[-1].drop_tree()
        article.props.text = article.doc.cssselect("#detailContentBlock div.pText")
        if article.doc.cssselect("#detailContentBlock p.bold"):
            article.props.kicker = article.doc.cssselect("#detailContentBlock p.bold")[0].text
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(HeuteScraper)


