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
from amcat.scraping.document import HTMLDocument, IndexDocument
import urllib2
from urlparse import urljoin
from amcat.tools.toolkit import readDate

INDEX_URL = "http://www.nu.nl/zoeken/?site=nu&page={p}&q={d}+{m}+{y}"
MONTHS = [
    'januari',
    'februari',
    'maart',
    'april',
    'mei',
    'juni',
    'juli',
    'augustus',
    'september',
    'oktober',
    'november',
    'december'
]

from urllib2 import HTTPError

class NuScraper(HTTPScraper, DatedScraper):
    medium_name = "Nu.nl"

    def _get_units(self):
        url_formats = {
            'd' : self.options['date'].day,
            'm' : MONTHS[self.options['date'].month-1],
            'y' : self.options['date'].year,
            'p' : 0
            }

        doc = self.getdoc(INDEX_URL.format(**url_formats))
        while doc.cssselect("div.searchResultItem"):
            for unit in doc.cssselect("div.searchResultItem"):
                a = unit.cssselect("div.title a")[0]
                if "NU TV Gids" in a.text_content() or not(unit.cssselect("div.updatedAt")):
                    continue
                
                date =readDate(unit.cssselect("div.updatedAt")[0].text_content().lstrip("Latse upd"))

                    
                yield HTMLDocument(url=a.get('href'), headline = a.text, date = date)
            if doc.cssselect("div.pagination"):
                url_formats['p'] += 1
                doc = self.getdoc(INDEX_URL.format(**url_formats))
            else:
                break
                                

    def _scrape_unit(self, page):
        try:
            page.prepare(self)
        except HTTPError:
            return
        error = page.doc.cssselect(".errorview")
        if error:
            return
        date = readDate(page.doc.cssselect("div.dateplace-data")[0].text_content().split("\n")[1])
        if date.date() != self.options['date']: 
            # nu.nl search sometimes returns wrong results
            return
        page.props.author = page.doc.cssselect("#leadarticle span.smallprint")[0].text.split("Door:")[1].strip()
        page.props.headline = page.doc.cssselect("#leadarticle .header h1")[0].text
        ads = page.doc.cssselect("center.articlebodyad")
        if ads:
            for i in range(len(ads)):
                ads[i].drop_tree() 
        page.props.text = page.doc.cssselect("#leadarticle .content")[0].text_content()
        yield page

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(NuScraper)
    
