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

import re
from datetime import timedelta, datetime
from lxml import html

from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.scraping.document import HTMLDocument
from urlparse import urljoin
from amcat.tools.toolkit import readDate

from urllib2 import HTTPError

class NuScraper(HTTPScraper, DatedScraper):
    medium_name = "Nu.nl"
    index_url = "http://www.nu.nl"

    def _get_units(self):
        for category_url in self.get_categories():
            category_doc = self.getdoc(category_url)
            first_article_url = urljoin(category_url, 
                                        category_doc.cssselect("#middlecolumn div.subarticle a")[0].get('href'))
            for url, doc in self.iterate_articles(first_article_url):
                yield (url, doc)

    def get_categories(self):
        categories = []
        index_doc = self.getdoc(self.index_url)
        main_categories = index_doc.cssselect("#mainmenu ul.listleft > li")
        for li in main_categories[2:]:
            categories.append(li.cssselect("a")[0].get('href'))
        skip = ['nufoto','weer/index','verkeer/index','socialtools','colofon']
        for href in categories:
            if all([(s not in href) for s in skip]):
                yield urljoin(self.index_url, href)

    def iterate_articles(self, next_url):
        """iterate over articles using the 'last article' button continuously"""
        urls = [next_url]
        d = self.options['date']
        self.date = datetime(d.year, d.month, d.day)
        while self.date.date() >= self.options['date']:
            doc = self.getdoc(next_url)
            if doc.cssselect("div.dateplace div.dateplace-data"):
                date_str = re.search("([0-9]{1,2} (januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december) [0-9]{4} [0-9]{2}\:[0-9]{2})", doc.cssselect("div.dateplace div.dateplace-data")[0].text).group(1)
            self.date = readDate(date_str)
            if self.date.date() == self.options['date']:
                yield next_url, doc
            next_url = urljoin(
                next_url, 
                [a.get('href') for a in doc.cssselect("div.widgetsection a.trackevent") if a.get('data-trackeventaction') == "vorig_artikel"][0])
            if next_url in urls:
                #sadly, sometimes there is a loop
                break
            urls.append(next_url)

    def _scrape_unit(self, urldoc):
        article = HTMLDocument(url = urldoc[0])
        article.doc = urldoc[1]
        article.props.date = self.date
        article.props.headline = article.doc.cssselect("div.header h1")[0].text
        article.props.text = article.doc.cssselect("div.content h2, div, p")
        article.props.author = article.doc.cssselect("span.smallprint")[0].text_content()
        if "|" in article.props.author:
            article.props.author = article.props.author.split('|')[0]
        if 'nuzakelijk.nl' in urldoc[0]:
            article.props.section = article.doc.cssselect("#articlebody a.category")[-1].text
        else:
            article.props.section = article.doc.cssselect("#categoryheader h2 a")[-1].text
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(NuScraper)
    
