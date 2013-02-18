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

class GezondheidblogCrawler(Crawler):
    medium_name = "gezondheid.blog.nl"
    allow_url_patterns = [
        re.compile("gezondheid.blog.nl")
        ]

    ignore_url_patterns = [
        ]

    article_pattern = re.compile("gezondheid.blog.nl/[a-z]+/[0-9]{4}/[0-9]{2}/[0-9]{2}/[a-zA-Z0-9\-_]+")

    initial_urls = [
        "http://gezondheid.blog.nl"
        ]

    def __init__(self, *args, **kwargs):
        super(GezondheidblogCrawler, self).__init__(*args, **kwargs)
        
    def _scrape_unit(self, url): 
        page = HTMLDocument(url=url)
        page.prepare(self)
        for comment in self.get_comments(page):
            yield comment
        yield self.get_article(page)

    def get_article(self, page):
        postinfo = page.doc.cssselect("div.postInfo")[0].text
        page.props.date = readDate(postinfo.split(" op ")[1].split(",")[0])
        page.props.headline = page.doc.cssselect("div.postInner h1")[0].text_content()
        page.props.text = page.doc.cssselect("div.postEntry")[0]
        page.props.author = postinfo.split(" op ")[0].split("Door")[1]
        return page

    def get_comments(self, page):
        for li in page.doc.cssselect("ul.commentlist li.comment"):
            comment = HTMLDocument()
            comment.parent = page
            try:
                dateauthor = li.cssselect("div.commentsbox")[0].text_content()
            except IndexError:
                comment.props.author = li.text_content().split(":")[0]

                comment.props.date = readDate(":".join(li.text_content().split(":")[1:2]))
                try:
                    comment.props.text = li.cssselect("div.comment-text-reply")[0]
                except UnicodeDecodeError:
                    continue
            else:
                comment.props.author = dateauthor.split("Geplaatst door")[1].split(" op ")[0]
                try:
                    li.cssselect("div.commentsbox a")[0].drop_tree()
                except:
                    pass
                comment.props.date = readDate(dateauthor.split(" op ")[1])
                try:
                    comment.props.text = li.cssselect("div.comment-text")[0]
                except UnicodeDecodeError:
                    continue
            yield comment


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(GezondheidblogCrawler)


