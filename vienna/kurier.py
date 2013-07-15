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

from urllib2 import URLError
from urlparse import urljoin
import re
from datetime import date

from amcat.scraping.document import Document, HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper #choose one
from amcat.tools.toolkit import readDate

class KurierScraper(HTTPScraper, DatedScraper):
    medium_name = "kurier.at"
    index_url = "http://kurier.at"

    def _get_units(self):
        for url, doc in self.getdocs():
            date = readDate(doc.cssselect("section.headlinedivider p.lfloat")[0].text_content().strip().split("am")[1])
            print(date)
            if date.date() != self.options['date']:
                continue
            article = HTMLDocument(url = url, date = date)
            article.doc = doc
            yield article

    def getdocs(self):
        urls = ["http://kurier.at/wirtschaft","http://kurier.at/politik"]
        done = set(urls)
        n_urls_back = (date.today() - self.options['date']).days * 100 + 100
        n_urls_back = n_urls_back < 1000 and n_urls_back or 1000
        print(n_urls_back)
        for x in range(n_urls_back):
            url = urls.pop(0)
            p = "^http://kurier.at/(wirtschaft|politik)/[a-zA-Z0-9]+/.+/[0-9\.]+$"
            try:
                doc = self.getdoc(url)
            except URLError:
                continue
            if re.match(p, url):
                yield url, doc
            for href in [a.get('href') for a in doc.cssselect("a") if a.get('href')]:
                url = urljoin(url, href.strip())
                if ('wirtschaft' in url or 'politik' in url or 'meinung' in url) and '#' not in url and url not in done and url.startswith("http://kurier.at") and '/kurs/' not in url and '/print' not in url:
                    done.add(url)
                    urls.append(url)

    def _scrape_unit(self, article):
        article.props.section = " > ".join(article.props.url.split("/")[2:4])
        article.props.headline = article.doc.cssselect("h1.cdark span")[0].text_content().strip()
        if article.doc.cssselect("h1.cdark span.posttitle"):
            article.props.byline = article.doc.cssselect("h1.cdark span.posttitle")[0].text_content().strip()
        article.props.externalid = int("".join(article.props.url.split("/")[-1].split(".")))
        article.props.text = article.doc.cssselect("section.inner div.textsection")
        if article.doc.cssselect("div editedBy font"):
            article.props.author = article.doc.cssselect("div.editedBy font")[0].text_content().strip()
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(KurierScraper)


