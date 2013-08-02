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
from datetime import datetime
from urllib2 import HTTPError

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate

class ViennaScraper(HTTPScraper, DatedScraper):
    medium_name = "vienna.at"
    website = "vienna.at"
    index_url = "http://www.{self.website}/date/{self.options[date].year}/{self.options[date].month:02d}/page/{pagenr}"

    def _get_units(self):
        index_doc = self.getdoc(self.index_url.format(pagenr = 1, **locals()))
        for page_doc in self.getpages(index_doc):
            for div in page_doc.cssselect("div.NewsIndex div.Article"):
                timetag = div.cssselect("span.TimeDiff")[0].getchildren()[0].text
                timestamp = re.search("from: ([0-9]+) {1,2}to", timetag).group(1)
                article_url = urljoin(page_doc.base_url, div.cssselect("h3.Black a")[0].get('href'))

                date = datetime.fromtimestamp(float(timestamp))
                if date.date() == self.options['date']:
                    yield HTMLDocument(
                        url = article_url,
                        date = date,
                        headline = div.cssselect("h3.Black a")[0].text,
                        externalid = article_url.split("/")[-1].split("-")[-1],
                        )
                elif date.date() < self.options['date']:
                    return

    def getpages(self, index):
        yield index
        #debug
        return
        pagenr = 1
        while True:
            pagenr += 1
            try:
                yield self.getdoc(self.index_url.format(**locals()))
            except HTTPError:
                break

    def _scrape_unit(self, article):
        article.prepare(self)
        breadcrumbs = article.doc.cssselect("div.BreadCrumbs span:not(.Separator)")[1:-1]
        article.props.section = " > ".join([span.text_content().strip() for span in breadcrumbs])
        if "Bezirk" in article.props.section:
            article.props.bezirk = article.props.section.split(".")[0].strip()
            article.props.section = "Bezirk"
        article.props.text = article.doc.cssselect("div.Article #article_lead")
        bodytext = article.doc.cssselect("#BodyText")[0]
        wrapper = bodytext.cssselect("div.SingleContentWrapper-450px")[0]
        for tag in wrapper.iter():
            #removing html comments and other clutter
            if callable(tag.tag):
                tag.drop_tree()
        lastdiv = wrapper.cssselect(".SingleContentWrapper-450px > div")
        if lastdiv and "zum thema" in lastdiv[0].text_content():
            lastdiv[0].drop_tree()

        article.props.text += wrapper
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(ViennaScraper)


