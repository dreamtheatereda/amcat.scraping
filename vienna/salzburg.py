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

import json
import math

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate

class SalzburgScraper(HTTPScraper, DatedScraper):
    medium_name = "Salzburger Nachrichten"
    solr_url = "http://search.salzburg.com/news/solr/sn/select?sort=date%20desc&q={{!boost%20b%3D%24dateboost%20v%3D%24qq}}&facet.date.start=1997-01-01T00%3A00%3A00Z%2FDAY&facet.date.end=NOW%2FDAY%2B1DAY&facet.date.gap=%2B1MONTH&qq=*%3A*&wt=json&start={offset}"

    def _get_units(self):
        d = self.options['date']
        n_articles = self.getresponse(0)["numFound"]
        offset = self.find_start(n_articles)
        while True:
            docs = self.getresponse(offset)["docs"]
            for data, date in [(doc, readDate(doc['date']).date()) for doc in docs]:
                if date < d:br = 1;break
                elif date == d and 'text' in data.keys(): yield data
            if 'br' in locals().keys():break
            offset += 10

    def find_start(self, n_articles):
        """Intelligently find the page at which the articles are for the given date, saves hours"""
        jump_distance = n_articles / 4.
        index = n_articles / 2
        offset = int(math.ceil((index) / 10) * 10)
        #find an article with the right date
        while True:

            offset = int(math.ceil(index / 10) * 10)
            docs = self.getresponse(offset)["docs"]
            dates = [readDate(d["date"]).date() for d in docs]

            if self.options['date'] in dates:
                break
            elif self.options['date'] > dates[0]:
                index -= jump_distance
            elif self.options['date'] < dates[0]:
                index += jump_distance

            if jump_distance < 10: return 0
            jump_distance /= 2.

        #go back to first occurrence
        i = 0
        while self.options['date'] in dates:
            i += 1
            offset -= 10 * i 
            if offset < 0: return 0
            docs = self.getresponse(offset)["docs"]
            dates = [readDate(d["date"]).date() for d in docs]
        return offset

    def getresponse(self, offset):
        _json = self.open(self.solr_url.format(**locals())).read()
        return json.loads(_json)["response"]

    article_url = "http://www.salzburg.com/nachrichten/id=112&tx_ttnews%5Btt_news%5D={urlid}&cHash=abc"

    def _scrape_unit(self, data):
        urlid = data['uri'].split('-')[-1]
        article_url = self.article_url.format(**locals())
        yield HTMLDocument(
            date = readDate(data['date']),
            section = ", ".join('ressort' in data.keys() and data['ressort'] or []),
            headline = data['title'],
            url = article_url
            externalid = data['id'],
            text = data['text'],
            author = data['author'],
            tags = 'tag' in data.keys() and data['tag'],
            teaser = 'teaser' in data.keys() and data['teaser'],
            all_data = data
            )

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(SalzburgScraper)


