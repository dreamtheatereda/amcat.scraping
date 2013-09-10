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
from datetime import date, timedelta

from amcat.scraping.document import Document, HTMLDocument
from amcat.tools.toolkit import readDate

BASE_URL = "http://www.powned.tv"
ARCHIVE_URL = "http://www.powned.tv/archief/{d.year:04d}/{d.month:02d}/{x:02d}-week/"

from amcat.scraping.scraper import HTTPScraper,DatedScraper

class PownewsScraper(HTTPScraper, DatedScraper):
    medium_name = "PowNews"

    def _get_units(self):
        self.open("http://www.powned.tv")
        self.open("http://cookies.publiekeomroep.nl/accept/")
        d = self.options['date']
        docs = []
        for x in range(d.day - 7, d.day + 7):
            archive_url = ARCHIVE_URL.format(**locals())
            try:
                doc = self.getdoc(archive_url)
            except HTTPError:
                pass
            else:
                docs.append(doc)

        entries = set([])
        for doc in docs:
            for li in doc.cssselect("ul.articlelist li"):
                entries.add(li)

        for li in entries:
            datestr = " ".join(li.cssselect("span.t")[0].text.split()[:2]) + " " + str(self.options['date'].year)
            _date = readDate(datestr).date()
            if _date == self.options['date']:
                article = HTMLDocument(
                    date = _date,
                    url = urljoin(archive_url, li.cssselect("a")[0].get('href')))
                yield article

    def _scrape_unit(self, article):        
        article.prepare(self)
        article = self.get_article(article)
        for comment in self.get_comments(article):
            comment.is_comment = True
            yield comment
        yield article

    def get_article(self, page):
        page.props.author = page.doc.cssselect("#artikel-footer .author-date")[0].text.split("|")[0].strip()
        page.props.headline = page.doc.cssselect("div.acarhead h1")[0].text
        page.props.text = [page.doc.cssselect("div.artikel-intro")[0], page.doc.cssselect("div.artikel-main")[0]]
        page.props.section = page.props.url.split("/")[4]
        return page

    def get_comments(self,page):
        for div in page.doc.cssselect("#comments div.comment"):
            comment = HTMLDocument(parent = page)
            comment.props.section = page.props.section
            comment.props.url = page.props.url
            comment.props.text = div.cssselect("p")[0]
            footer = div.cssselect("p.footer")[0].text_content().split(" | ")
            comment.props.author = footer[0].strip()
            comment.props.date = readDate(footer[1].strip())
            yield comment
                                         




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(PownewsScraper)


