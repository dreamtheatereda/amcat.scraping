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

from math import ceil
import re
from urlparse import urljoin
from datetime import timedelta

from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.scraping.document import HTMLDocument
from amcat.tools.toolkit import readDate


class NuScraper(HTTPScraper, DatedScraper):
    medium_name = "nu.nl - website"
    search_url = "http://www.nu.nl/zoeken/?q=&limit=50&page={p}"

    def _get_units(self):
        initial_url = self.search_url.format(p = 1)
        initial_doc = self.getdoc(initial_url)
        dates = [readDate(article.cssselect("span.date")[0].text).date() for article in initial_doc.cssselect("div.subarticle")]
        self.maxdate = max(dates)
        n_results = int(initial_doc.cssselect("#searchlist header h1")[0].text.strip().split(" ")[-1])
        for page in self.pinpoint_pages(n_results):
            for div in page.cssselect("div.subarticle"):
                date = readDate(div.cssselect("span.date")[0].text).date()
                if date == self.options['date']:
                    url = div.cssselect("h2 a")[0].get('href')
                    yield (date, url)
        
    def pinpoint_pages(self, n_results):
        #loading a single page takes a long time so we're using a smarter algorithm
        n_pages = int(ceil(n_results / 50.))
        pointer = n_pages / 2.
        jump_distance = n_pages / 4.
        while True:
            p = int(pointer)
            print("Inspecting page {p} of search results...".format(**locals()))
            dates, page = self.page_has_articles(p)
            if page:
                print("Page with correct date found!")
                anchor = p
                break
            elif dates[0] < self.options['date']:
                #if articles too old, jump a few pages back
                pointer -= jump_distance
            elif dates[0] > self.options['date']:
                #if articles too young, jump a few pages forward
                pointer += jump_distance
            jump_distance /= 2.

            if jump_distance < .1:
                raise Exception("No articles found for given date")
        if self.options['date'] >= self.maxdate - timedelta(days = 1):
            raise Exception("Archive not yet filled up")


        #check back for first page with given date
        i = 1
        while p >= 0:
            p -= i
            i += 1
            d, page = self.page_has_articles(p)
            if not page:
                break
            
        #check forward
        while True:
            p += 1
            d, page = self.page_has_articles(p)
            if page:
                yield page
            elif p < anchor:
                pass
            else:
                break

    def page_has_articles(self, p):
        page = self.getdoc(self.search_url.format(**locals()))
        articles = page.cssselect("div.subarticle")
        dates = [readDate(article.cssselect("span.date")[0].text).date() for article in articles]
        if max(dates) > self.maxdate:
            self.maxdate = max(dates)
        if any([date == self.options['date'] for date in dates]):
            return dates, page
        else:
            return dates, None


    def _scrape_unit(self, date_url):
        date, url = date_url
        article = HTMLDocument(url = url, date = date)
        article.prepare(self)
        article.props.headline = article.doc.cssselect("#leadarticle div.header h1")[0].text_content().strip()
        article.props.section = url.split("/")[3].upper()
        article.props.summary = article.doc.cssselect("#leadarticle div.content h2.summary")
        article.doc.cssselect("center.articlebodyad")[0].drop_tree()
        article.props.text = article.doc.cssselect("#leadarticle div.content")
        smallprint = article.doc.cssselect(
            "#leadarticle div.content span.smallprint")[0].text_content().split("|")[0]
        article.props.author = smallprint.split("Door:")[1].strip()
        article.props.tags = [a.text_content() for a in article.doc.cssselect("#middlecolumn div.tags li a")]
        yield article


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping")
    cli.run_cli(NuScraper)
    
