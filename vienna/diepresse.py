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
from amcat.scraping.scraper import HTTPScraper,DatedScraper

class DiePresseScraper(HTTPScraper, DatedScraper):
    medium_name = "diepresse.com"
    index_url = "http://diepresse.com/user/search.do?detailForm=true&switch=true&showDetailForm=true"
    search_url = "http://diepresse.com/user/search.do?resultsPage={page}&dayOnly={self.options[date].day}&monthOnly={self.options[date].month}&yearOnly={self.options[date].year}&zeitpunkt=6"

    def _get_units(self):
        self.open(self.index_url)
        for page in self.getpages():
            for li in page.cssselect("#content ol.searchlist li"):
                yield li

    def getpages(self):
        page = 0
        while True:
            page += 1
            doc = self.getdoc(self.search_url.format(**locals()))
            
            if not doc.cssselect("#content ol.searchlist li"):
                break
            yield doc

    def _scrape_unit(self, li):
        a = li.cssselect("li > a")[0]
        article = HTMLDocument(url = urljoin(self.index_url, a.get('href')))
        article.props.headline = a.text
        article.props.kicker = li.cssselect("div.infoboard a.kicker")[0].text
        article.props.intro = li.cssselect("p")
        article.props.date = readDate(li.cssselect("div.infoboard span.time")[0].text_content())
        article.prepare(self)
        articletime = article.doc.cssselect("p.articletime")[0].text_content()
        if len(articletime.split("|")) > 2:
            article.props.date = readDate(" ".join(articletime.split("|")[:-1]))
            article.props.author = articletime.split("|")[-1]
        else:
            article.props.author = articletime.strip()
            if " Korrespondent" in article.props.author:
                article.props.author = article.props.author.split("Korrespondent")[1].strip()

        for ad in article.doc.cssselect("div.noprint"):
            ad.drop_tree()
        article.props.text = article.doc.cssselect("p.articlelead, #articletext")
        article.props.section = article.doc.cssselect("div.headtop span.sitetop")[0].text_content()
        yield article
        #NOTE: comments are not scraped as requested
        
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(DiePresseScraper)


