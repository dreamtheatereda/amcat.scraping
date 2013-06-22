#!/usr/bin/python
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
from amcat.tools import toolkit
from amcat.scraping.toolkit import todate
from urlparse import urljoin

class SpitsnieuwsScraper(DatedScraper, HTTPScraper):
    medium_name = "Spits - website"
    index_url = "http://www.spitsnieuws.nl/archives/{self.date.year:04d}{self.date.month:02d}"
    def _get_units(self):
        self.date = self.options['date']
        url = self.index_url.format(**locals())
        first = self.getdoc(url)
        for doc in self.get_pages(first):
            for li in doc.cssselect('div.item-list-archive ul li.views-row'):
                docdate = toolkit.readDate(li.text.strip('\n\r \u2022:')).date()
                if docdate == todate(self.date):
                    href = li.cssselect('a')[0].get('href')
                    href = urljoin(url, href)
                    yield HTMLDocument(url=href)
                elif docdate < todate(self.date):
                    return


    def get_pages(self, doc):
        page_url = self.index_url + "?page={pagenum}"
        yield doc
        pagenum = 1
        last_page = int(doc.cssselect("li.pager-last a")[0].get('href').split("=")[1])
        while pagenum <= last_page:
            url = page_url.format(**locals())
            yield self.getdoc(url)
            pagenum += 1

    def _scrape_unit(self, doc):
        doc.doc = self.getdoc(doc.props.url)
        doc.props.headline = doc.doc.cssselect('#node h1')[0].text_content()
        doc.props.text = doc.doc.cssselect('div.article')[0]
        doc.props.section = doc.props.url.split("/")[4]
        footer = doc.doc.cssselect('div.article-options')[0].text_content().split('|')
        doc.props.author = footer[0].strip()
        doc.props.date = toolkit.readDate(" ".join(footer[1:3]))
        for c in self.comments(doc):
            c.props.parent = doc
            c.is_comment = True
            yield c


        yield doc

    def comments(self, doc):

        divs = doc.doc.cssselect('.comment')

        for div in divs:
            comm = doc.copy()
            comm.props.headline = "re: {}".format(doc.props.headline)
            comm.props.text = div.cssselect('p')
            comm.props.author = div.cssselect('strong')[0].text

            dt = " ".join(div.cssselect("ul")[0].text_content().split("|")[1:-1])
            comm.props.date = toolkit.readDate(dt)
            yield comm

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(SpitsnieuwsScraper)
