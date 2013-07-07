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

from urllib2 import HTTPError, URLError
from urlparse import urljoin

from amcat.tools.toolkit import readDate
from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper


class OrfAtScraper(HTTPScraper, DatedScraper):
    medium_name = "orf.at"
    index_url = "http://news.orf.at"
    articles = {}

    def _get_units(self):
        urls = set([self.index_url])
        #gather a good amount of urls crawler style, 3 links deep
        for x in range(3):
            for url in urls:
                doc = self.getdoc(url)
                if doc:
                    to_add = [urljoin(self.index_url, a.get('href'))
                              for a in doc.cssselect("a")
                              if a.get('href') and "/stories/" in a.get('href')]
            urls.update(to_add)

        #find more articles by counting up and down the article indices
        for url in urls:
            self.findarticles(url)

        for article in self.articles.items():
            yield article

    def findarticles(self, url):
        try:
            index = int(url.split("/")[-2])
        except ValueError:
            return
        pointer = index; i = 0
        url = "/".join(url.split("/")[:-2]) + "/"
        #count down
        while True:
            pointer -= 1
            article_url = url + str(pointer) + "/"
            date = self.date(self.getdoc(article_url))
            if date and date < self.options['date']:
                break
            if article_url in self.articles.keys():
                break
            if not date:
                i += 1
            if i > 10:
                break

        #count up
        pointer = index; i = 0
        while True:
            pointer += 1
            article_url = url + str(pointer) + "/"
            date = self.date(self.getdoc(article_url))
            if date and date > self.options['date']:
                break
            if article_url in self.articles.keys():
                break
            if not date:
                i += 1
            if i > 10:
                break
            

    def date(self, doc):
        if doc:
            if doc.cssselect("p.date"):
                try:
                    date = readDate(doc.cssselect("p.date")[0].text)
                except ValueError:
                    return
                if date:
                    return date.date()

    def getdoc(self, url):
        try:
            doc = super(OrfAtScraper, self).getdoc(url)
        except Exception:
            return
        if doc.cssselect("p.date"):
            date = readDate(doc.cssselect("p.date")[0].text_content())
            if date and date.date() == self.options['date']:
                self.articles[url] = doc
        return doc

    def _scrape_unit(self, item):
        url, doc = item
        article = HTMLDocument(url = url)
        article.props.headline = doc.cssselect("div.storyText h1")[0].text_content()
        article.props.text = doc.cssselect(".storyText")
        article.props.date = self.date(doc)
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(OrfAtScraper)


