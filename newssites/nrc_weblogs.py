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

from amcat.scraping.document import Document, HTMLDocument

from urlparse import urljoin
from amcat.tools.toolkit import readDate
from urllib2 import HTTPError

INDEX_URL = "http://www.nrc.nl/{}/"

from amcat.scraping.scraper import HTTPScraper,DatedScraper

class WeblogNRCScraper(HTTPScraper, DatedScraper):
    medium_name = "NRC website - blogs"
    t = "weblogs"
    nextcheckt = False
    def __init__(self, *args, **kwargs):
        super(WeblogNRCScraper, self).__init__(*args, **kwargs)

    def _get_units(self):

        url = INDEX_URL.format(self.t)
        index = self.getdoc(url) 
        
        for unit in index.cssselect('div.voorjekijkendoorlopen h2'):
            href = unit.cssselect('a')[0].get('href').lstrip("/.")
            url = urljoin("http://www.nrc.nl/",href)
            y = self.options['date'].year
            m = self.options['date'].month

            link = urljoin(url,"{y:04d}/{m:02d}/".format(**locals()))
            try:
                self.open(link)
            except HTTPError: #not up to date
                continue
            yield link
            

    def _scrape_unit(self, url):
        doc = self.getdoc(url)
        tag = "dt"
        for d_ in doc.cssselect("div.lijstje dt,dd"):
            if tag == "dt":
                time = readDate(d_.cssselect("time")[0].get('datetime'))
                if time.date() < self.options['date']:
                    break
                elif time.date() == self.options['date']:
                    get = True
                elif time.date() > self.options['date']:
                    get = False
                tag = "dd"
            elif tag == "dd":
                if get == True:
                    article_url = urljoin(url, d_.cssselect("a")[0].get('href'))
                    article = self.get_article(article_url, time)
                    for comment in self.get_comments(article):
                        yield comment
                    yield article
                tag = "dt"
                    



    def get_article(self, url, datetime):
        page = HTMLDocument(url = url)
        page.prepare(self)
        page.props.headline = page.doc.cssselect("div.article h1")[0]
        page.props.text = page.doc.cssselect("#broodtekst")[0]
        page.props.date = datetime
        if page.doc.cssselect("div.auteursinfo"):
            page.props.author = page.doc.cssselect("div.auteursinfo h2")[0].text_content()
        page.props.section = url.split("/")[3]
            
        return page

    def get_comments(self,page):
        for div in page.doc.cssselect("div.comment"):
            comment = Document()
            comment.props.text = div.cssselect("div.reactie")[0]
            comment.props.author = div.cssselect("li.naam")[0].text_content()
            comment.props.date = readDate(div.cssselect("li.date")[0].text_content())
            comment.parent = page
            yield comment




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WeblogNRCScraper)


