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

from amcat.scraping.scraper import ArchiveForm
from amcat.scraping.googlescraper import GoogleScraper

from amcat.tools.toolkit import readDate
from amcat.scraping.document import HTMLDocument

from datetime import timedelta

def makequery(date):
    months_abbrev = [
        'jan','feb','mrt','apr',
        'mei','jun','jul','aug',
        'sep','okt','nov','dec'
        ]

    return "site:http://www.telegraaf.nl \"{:02d} {} {:04d}\"".format(
        date.day,
        months_abbrev[date.month],
        date.year)

class WebTelegraafArchiveScraper(GoogleScraper):
    medium_name="telegraaf.nl"
    options_form = ArchiveForm
    
    def get_units(self):
        self.date = self.options['first_date']
        while self.date <= self.options['last_date']:
            self.query = makequery(self.date)
            for unit in super(WebTelegraafArchiveScraper,self).get_units():
                yield unit
            self.date += timedelta(days=1)

    def _scrape_unit(self, page):
        page.props.date = readDate(page.doc.cssselect("span.datum")[0].text_content())
        page.props.author = "Unknown"
        page.props.headline = page.doc.cssselect("#artikel h1")[0].text_content().strip()
        page.doc.cssselect("div.broodMediaBox")[0].drop_tree()
        page.props.text = page.doc.cssselect("#artikelKolom")[0].text_content()
        yield page

        def scrape_comments(self,page):
            url = page.doc.cssselect("ul.pager li.pager-last")[0].text
            p = url.split("page=")[0]+"page={}"
            docs = [self.getdoc(p.format(x)) for x in range(int(url.split("page=")[-1]))]
            for doc in docs:
                for div in doc.cssselect("#comments div.comment"):
                    comment = Document()
                    comment.props.text = div.cssselect("div.content")[0].text_content()
                    comment.props.author = div.cssselect("span.submitted-username")[0].text_content()
                    comment.props.date = readDate(div.cssselect("div.submitted div.floatr")[0])
                    comment.parent = page
                    yield comment




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WebTelegraafArchiveScraper)
