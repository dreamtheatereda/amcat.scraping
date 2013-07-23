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

from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument

from urllib2 import HTTPError
from urlparse import urljoin
from datetime import datetime

INDEX_URL = "http://www.rtlnieuws.nl/"

class RTLScraper(HTTPScraper, DatedScraper):
    medium_name = "RTL Nieuws"

    def _get_units(self):
        self.open(INDEX_URL)
        self.opener.opener.addheaders.append(('Cookie','rtlcookieconsent=yes'))
        index = self.getdoc(INDEX_URL) 
        sections = []
        for li in index.cssselect("#mainNav li.expanded")[:4]:
            sections.extend(li.cssselect("li.leaf"))
        self.stories = set([])
        for li in sections:
            section_url =  urljoin(INDEX_URL, li.cssselect("a")[0].get('href'))
            for article in self.getarticles(section_url):
                article.props.section = li.text_content().strip()
                yield article
                
        for url in self.stories:
            for article in self.getarticles(url):
                article.props.section = article.props.url.split("/")[-2]
                yield article

    def getarticles(self, url):
        url += "?page={i}"
        i = 0
        _date = self.options['date']
        while _date >= self.options['date']:
            articles = list(self.extract_articles(url.format(**locals())))
            i += 1
            if not articles:
                break
            for article in articles:
                _date = article.props.date.date()
                if _date == self.options['date']:
                    yield article
                elif _date < self.options['date']:
                    break

    def extract_articles(self, url):
        try:
            doc = self.getdoc(url)
        except HTTPError:
            return
        for tag in doc.cssselect("#main article.news"):
            if 'poll' in tag.get('class'):
                continue
            _date = datetime.fromtimestamp(int(tag.get('created')))
            article = HTMLDocument(date = _date)
            if tag.cssselect("div.tweet"):
                article.props.type = "tweet"
                article.props.text = tag.cssselect("p")[0]
                article.props.author = article.props.text.cssselect("b a")[0].get('title')
                article.props.url = url.split("?")[0]
            elif tag.cssselect("div.quoteBody"):
                article.props.type = "quote"
                a = tag.cssselect("div.quoteBody a")[0]
                article.props.text = a.text_content()
                article.props.url = urljoin(url, a.get('href'))
                article.props.author = tag.cssselect("span.author")[0].text.strip()
            elif tag.cssselect("div.videoContainer") or 'promo' in tag.get('class'):
                continue
            elif tag.cssselect("div.tagline h4"):
                self.stories.add(urljoin(url, tag.cssselect("h4 a")[0].get('href')))
                continue
            else:
                h = tag.cssselect("div.body h3")[0]
                article.props.type = "article"
                article.props.headline = h.text_content().strip()
                if h.cssselect("a"):
                    article.props.url = urljoin(url, h.cssselect("a")[0].get('href'))
                else:
                    article.props.url = url
            yield article

    def _scrape_unit(self, article):
        if article.props.type == "article":
            article.prepare(self)
            [div.drop_tree() for div in article.doc.cssselect("div.rtldart")]
            article.props.text = article.doc.cssselect("article.news div.body div.paragraph")
        print(article)
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(RTLScraper)

