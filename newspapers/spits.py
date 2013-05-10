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

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper,DatedScraper

from urllib import urlencode
from urllib2 import HTTPError
from datetime import date
import time
import re
#from amcat.tools.toolkit import readDate
#from amcat.scraping.tools import toolkit


class SpitsKrantScraper(HTTPScraper, DatedScraper):
    medium_name = "Spits"

    cookie_url = "http://tmgonlinemedia.nl/consent/consent/?return=http%3A%2F%2Fwww.spitsnieuws.nl%2F&clienttime={timestamp}&detect={detect}&version={version}"
    page_url = "http://krant.spitsnieuws.nl/spits/_main_/{y:04d}/{m:02d}/{d:02d}/{pagenum:03d}/page.html"
    article_url = "http://krant.spitsnieuws.nl/spits/_main_/{y:04d}/{m:02d}/{d:02d}/{pagenum:03d}/article/{articleid}.html"

    def accept_cookies(self):
        timestamp = int(time.time())
        get_params = {
            'timestamp' : timestamp,
            'detect' : 'true',
            'version' : 0
            }
        url = self.cookie_url.format(**get_params)
        csrf_token = self.getdoc(url).cssselect('#csrf_token')[0].get('value')
        post_params = {
            'advertising':'y',
            'advertising_network':'y',
            'advertising_targeting':'y',
            'analytics':'y',
            'csrf_token':csrf_token,
            'essential':'y',
            'functional':'y',
            'level':'cookie-level-3',
            'social':'y'
            }
        self.open(url, urlencode(post_params))

    def _get_units(self):
        self.accept_cookies()
        url_dict = {
            'y' : self.options['date'].year,
            'm' : self.options['date'].month,
            'd' : self.options['date'].day,
        }
        index_url = self.page_url.format(pagenum = 1, **url_dict)[:-9]
        try:
            index_doc = self.getdoc(index_url) 
        except HTTPError:
            raise ValueError("url {index_url} returns 404, perhaps it is a weekend day?".format(**locals()))
        sections = self.get_sections(index_doc)
        pages = [int(option.get('value')) for option in index_doc.cssselect(".select_page option")]
        for pagenum in pages:
            if pagenum in sections.keys():
                self.section = sections[pagenum]
            self.pagenum = pagenum
            page_url = self.page_url.format(pagenum = pagenum, **url_dict)
            page_doc = self.getdoc(page_url)
            article_ids = set([
                    int(div.get('class').lstrip("article"))
                    for div in page_doc.cssselect("#page div")
                    ])
            for url in [self.article_url.format(**dict(locals(), **url_dict))
                        for articleid in article_ids]:
                yield url

    def get_sections(self, doc):
        sections = {}
        table = doc.cssselect("td.nav table")[0]
        for tr in table.cssselect("> tr"):
            if "Secties" in tr.text_content():
                html = tr
                break
        for a in html.cssselect("a"):
            pagenum = int(a.get('href').split("/")[1])
            sections[pagenum] = a.text
        return sections
        
    def _scrape_unit(self, url):
        article = HTMLDocument(url = url, section = self.section)
        article.prepare(self)
        article.props.date = date(*[int(n) for n in url.split("/")[5:8]])
        article.props.pagenr = self.pagenum
        article.props.headline = article.doc.cssselect("#article h1")[0].text_content()
        article.props.text = article.doc.cssselect("div.body")[0]
        dateline_pattern = re.compile("^([A-Z]+( [A-Z]+)?)$")
        b = article.props.text.cssselect("b")
        if b and dateline_pattern.search(b[0].text_content()):
            article.props.dateline = dateline_pattern.search(b[0].text_content()).group(1)
            
        if article.doc.cssselect("#article address"):
            article.props.author = article.doc.cssselect("#article address")[0].text_content().lstrip("dor").strip()

        yield article


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping")
    cli.run_cli(SpitsKrantScraper)


