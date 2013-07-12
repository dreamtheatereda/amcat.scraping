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

INDEX_URL = "http://www.metronieuws.nl/rss/"

from django import forms
from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument

from amcat.tools import toolkit
from amcat.models.medium import Medium

from lxml import html
from urlparse import urljoin
import datetime

class MetroScraper(DatedScraper, HTTPScraper):
    medium_name = "Metro - website"
    
    def get_categories(self):
        """ Yields the urls to all the pages contianing the categories.
        """
        doc = self.getdoc(INDEX_URL)
        items = doc.cssselect("ul.list > li, ul.list > ul")
        for i,item in enumerate(items):
            if item.tag == 'li':
                if i == len(items) - 1:
                    href =  item.cssselect("a.rss")[0].get('href')
                    yield urljoin(INDEX_URL, href)
                    continue
                if items[i + 1].tag == 'ul':
                    for li in items[i + 1].cssselect("li"):
                        href = li.cssselect("a.rss")[0].get('href')
                        yield urljoin(INDEX_URL, href)
                else:
                    href = item.cssselect("a.rss")[0].get('href')
                    yield urljoin(INDEX_URL, href)


    def _get_units(self):
        for url in self.get_categories():
            doc = self.getdoc(url)
            for item in doc.cssselect("item"):
                date = toolkit.readDate(item.cssselect("pubdate")[0].text)
                if date.date() != self.options['date']:
                    continue
                link = item.cssselect("link")[0]
                doc = HTMLDocument(
                    url=urljoin(INDEX_URL, html.tostring(link).lstrip("<link>")),
                    date = date,
                    headline = item.cssselect("title")[0].text
                    )
                yield doc

    def _scrape_unit(self, doc):
        doc.prepare(self)
        doc.props.text = doc.doc.cssselect("div.article-body")
        print(doc.props.text)
        yield doc

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping")
    cli.run_cli(MetroScraper)

