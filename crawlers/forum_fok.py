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
from amcat.scraping.scraper import Crawler
import re
from amcat.tools.toolkit import readDate

class ForumFokCrawler(Crawler):
    medium_name = "fok.nl forum"
    allow_url_patterns = [
        re.compile("forum.fok.nl")
        ]

    ignore_url_patterns = [
        ]

    article_pattern = re.compile("")

    initial_urls = [
        "http://www.ad.nl"
        ]

    def __init__(self, *args, **kwargs):
        super(ADCrawler, self).__init__(*args, **kwargs)
        
    def _scrape_unit(self, url): 
        page = HTMLDocument(url=url)
        page.prepare(self)
        for comment in self.get_comments(page):
            yield comment
        yield self.get_article(page)

    def get_article(self, page):
        span = page.doc.cssselect("#detail_content span.author")[0]
        page.props.date = readDate(tostring(span).split("<br/>")[1])
        try:
            page.props.author = span.cssselect("a")[0].text
        except IndexError:
            try:
                page.props.author = tostring(span).split("<br/>")[0].split("oor:")[1].strip()[0:98]
            except IndexError:
                page.props.author = "unknown"
        try:
            page.props.source = tostring(span).split("<br/>")[1].split("bron:")[1]
        except IndexError:
            pass
        page.props.headline = page.doc.cssselect("h1")[0].text
        try:
            page.props.text = [page.doc.cssselect("#detail_content p.intro")[0], page.doc.cssselect("section.clear")[0]]
        except IndexError:
            page.props.text = page.doc.cssselect("#detail_content")[0]
        return page

    def get_comments(self, page):
        for li in page.doc.cssselect("#detail_reactions #reaction ul.clear li"):
            comment = HTMLDocument()
            comment.props.author = li.cssselect("cite")[0].text.strip()
            comment.props.text = li.cssselect("blockquote")[0]
            comment.props.date = readDate(li.cssselect("span.time")[0].text)
            comment.parent = page
            yield comment


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(ADCrawler)


