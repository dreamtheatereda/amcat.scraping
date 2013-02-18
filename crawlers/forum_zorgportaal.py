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
from amcat.scraping.scraper import Crawler
import re
from amcat.tools.toolkit import readDate
from urlparse import urljoin

class ZorgportaalForumCrawler(Crawler):
    medium_name = "gezondheid.blog.nl"
    allow_url_patterns = [
        re.compile("site.zorgportaal.nl")
        ]

    ignore_url_patterns = [
        re.compile("(site.zorgportaal.nl/index.php/^(blogs-en-forums|forum)/)"),
        re.compile("/home/log-in-pagina"),
        re.compile("\?start=\d+$"),
        re.compile("/unread$")
        ]

    article_pattern = re.compile("site.zorgportaal.nl/index.php/forum/[a-zA-Z0-9\-_]+/[0-9]+\-[a-zA-Z0-9\-_]+")

    initial_urls = [
        "http://site.zorgportaal.nl/blogs-en-forums/"
        ]

    def __init__(self, *args, **kwargs):
        super(ZorgportaalForumCrawler, self).__init__(*args, **kwargs)
        
    def _scrape_unit(self, url): 
        page = HTMLDocument(url=url)
        page.prepare(self)
        for entry in self.get_article(page):
            yield entry

    def get_article(self, page):
        page.props.title = page.doc.cssselect("div.kmsg-header h2")[0].text_content()
        page.props.text = page.doc.cssselect("table.kmsg")[0].cssselect("div.kmsgtext")[0]
        page.props.date = readDate(page.doc.cssselect("div.kmsg-header")[0].cssselect("span.kmsgdate")[0].get('title'))
        page.props.author = page.doc.cssselect("table.kmsg")[0].cssselect("li.kpost-username")[0].text_content()

        for _page in self.get_pages(page.doc):
            comments = _page.cssselect("table.kmsg")
            for x in range(len(comments)-1):
                yield self.get_comment(page, page.doc.cssselect("div.kmsg-header")[x+1],page.doc.cssselect("table.kmsg")[x+1])
        yield page

    def get_pages(self,doc):
        yield doc
        pages = doc.cssselect("ul.kpagination li")
        if len(pages)>2:
            for li in pages[2:]:
                url = urljoin("site.zorgportaal.nl",li.cssselect("a")[0].get('href'))
                yield self.getdoc(url)

    def get_comment(self, page, header,table):
        comment = HTMLDocument()
        comment.parent = page
        comment.props.date = readDate(header.cssselect("span.kmsgdate")[0].get('title'))
        comment.props.headline = header.cssselect("h2 span")[0].text_content()
        comment.props.author = table.cssselect("li.kpost-username")[0].text_content()
        comment.props.text = table.cssselect("div.kmsgtext")[0]
        return comment


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(ZorgportaalForumCrawler)


