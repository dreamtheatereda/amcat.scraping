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

#this piece makes it possible to quickly create a new scraper. As there are thousands of papers and other mediums out on the web, we can never have enough scrapers.

from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, IndexDocument

from urlparse import urljoin

INDEX_URLS = ["http://www.joop.nl/opinies/sort/date/time/week/"]
BROWSE_URL = "http://www.joop.nl/opinies/browse/{pagenum}/sort/date/time/week/"
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
    'novembter',
    'december'
]


class JoopScraper(HTTPScraper, DBScraper):
    medium_name = "Joop.nl"

    def __init__(self, *args, **kwargs):

        super(JoopScraper, self).__init__(*args, **kwargs)

    def _get_units(self):
        for x in range(len(self.getdoc(INDEX_URLS[0]).cssselect("ul.paginator li"))-2):
            INDEX_URLS.append(BROWSE_URL.format(pagenum=x))
            yield IndexDocument(page = x,url=INDEX_URLS[x],date=self.options['date'],doc=self.getdoc(INDEX_URLS[x]))
        
    def _scrape_unit(self, ipage):
        ipage.prepare(self)
        date_str = "{month} {day}, {year}".format(day = self.options['date'].day,month = MONTHS[self.options['date'].month-1],year = self.options['date'].year)
        for li in ipage.doc.cssselect("ul.opinionblogs li"):
            if date_str in li.cssselect("span.info")[0].text_content().split("|")[0]:
                a = li.cssselect("h2 a")[0]
                url = urljoin("http://www.joop.nl/",a.get('href'))
                page = HTMLDocument(date = ipage.props.date,url=url)
                page.prepare(self)
                page.doc = self.getdoc(page.props.url)
                yield self.get_article(page)
                ipage.addchild(page)

        yield ipage

    def get_article(self, page):
        page.props.author = page.doc.cssselect(".author_head .text h2")[0].text
        print(page.props.url)
        page.props.headline = page.doc.cssselect("#content .blogarticle h2")[0].text
        page.doc.cssselect("#content .blogarticle h2")[0].drop_tree()
        page.doc.cssselect("#socialbar")[0].drop_tree()
        page.props.text = page.doc.cssselect("#content .blogarticle")[0].text_content()
        page.coords = ""
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(JoopScraper)





