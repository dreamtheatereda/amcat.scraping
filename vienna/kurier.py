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

from amcat.scraping.document import Document, HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper #choose one
from amcat.tools.toolkit import readDate

class KurierScraper(HTTPScraper, DatedScraper):
    medium_name = "kurier.at"
    index_url = "http://kurier.at"

    def _get_units(self):
        for url, doc in self.getdocs():
            date = readDate(doc.cssselect("section.headlinedivider p.lfloat")[0].text_content().strip().split("am")[1])
            if date.date() != self.options['date']:
                continue
            article = HTMLDocument(url = url, date = date)
            article.doc = doc
            yield article

    def getdocs(self):
        old_set = set(["http://kurier.at/wirtschaft","http://kurier.at/politik"])
        for x in range(3):
            new_set = set([])
            for url in old_set:
                p = "http://kurier.at/(wirtschaft|politik)/[a-zA-Z0-9]/.+/[0-9\.]+"
                doc = self.getdoc(url)
                if re.match(p, url):
                    yield url, doc
                new_set.update([urljoin(url, a.get('href').strip()) for a in doc.cssselect("a")])
            old_set = new_set
        

    def _scrape_unit(self, article):
        article.props.section = " > ".join(article.props.url.split("/")[2:4])
        article.props.headline = article.doc.cssselect("h1.cdark span")[0].text_content().strip()
        article.props.byline = article.doc.cssselect("h1.cdark span.posttitle")[0].text_content().strip()
        article.props.externalid = article.props.url.split("/")[-1]
        article.props.text = article.doc.cssselect("section.inner div.textsection")
        article.props.author = article.doc.cssselect("div.editedBy font")[0].text_content().strip()
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(KurierScraper)


