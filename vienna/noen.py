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

class NoenScraper(HTTPScraper, DatedScraper):
    medium_name = "noen.at"
    initial_url = "http://noen.at"
    index_url = "http://noen.at/news/{category}/datum.={d.day:02d}-{d.month:02d}-{d.year:04d}/"

    def _get_units(self):
        init_doc = self.getdoc(self.initial_url)
        d = self.options['date']
        for category in [a.text for a in init_doc.cssselect("li.navibox a") if "/news/" in a.get('href')]:
            index_url = self.index_url.format(**locals())
            try:
                index_doc = self.getdoc(index_url)
            except HTTPError:
                continue
            for div in index_doc.cssselect("div.main div.blocknews"):
                a = div.cssselect("a.title")[0]
                article = HTMLDocument(
                    url = urljoin(index_url, a.get('href')),
                    section = category,
                    headline = a.text_content().strip(),
                    )
                yield article
                    

    def _scrape_unit(self, article):
        article.prepare(self)
        article.props.date = readDate(article.doc.cssselect("#artikelbox div.dateandmore")[0].text_content())
        if article.props.date.date() != self.options['date']:
            print('Faulty date')
            return
        article.doc.cssselect("#story div")[-1].drop_tree()
        article.props.text = article.doc.cssselect("#story")
        firstline = article.props.text[0].text_content().strip().split("\n")[0]
        if len(firstline.split()) <= 8 and "Von " in firstline: #at most 8 words
            article.props.author = firstline.split("Von ")[1]
        kurztext = article.doc.cssselect("#kurztext")
        article.props.byline = kurztext and kurztext[0].text_content().strip() or None
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(NoenScraper)


