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

from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, Document
from amcat.tools.toolkit import readDate

import re


class Gezondheid_blog_nlScraper(HTTPScraper, DatedScraper):
    medium_name = "gezondheid.blog.nl"
    archive_url = "http://gezondheid.blog.nl/{self.y:04d}/{self.m:02d}"
    page_url = archive_url + "/page/{pagenum}"

    def __init__(self, *args, **kwargs):
        super(Gezondheid_blog_nlScraper, self).__init__(*args, **kwargs)
        self.y = self.options['date'].year
        self.m = self.options['date'].month


    def _get_units(self):
        archive_url = self.archive_url.format(**locals())
        for page_url in self.get_pages(archive_url):
            for div in self.getdoc(page_url).cssselect("div.post"):
                article_url = div.cssselect("h1 a")[0].get('href')
                article = HTMLDocument(url = article_url)
                article.props.headline = div.cssselect("h1 a")[0].text_content().strip()
                footer = div.cssselect("div.postInfo")[0].text_content().strip()
                
                pattern = re.compile("Door ([ \w]+) op ([0-9a-z :]+),( in de categorie ([\w ]+))?")
                results = pattern.search(footer)
                                
                article.props.date = readDate(results.group(2))
                if article.props.date.date() < self.options['date']:
                    break
                elif article.props.date.date() > self.options['date']:
                    continue
                article.props.author = results.group(1)
                article.props.section = results.group(4)
                yield article
                
                                                
    def get_pages(self, url):
        pagenav = self.getdoc(url).cssselect("div.page_navi")[0]
        num = pagenav.cssselect("a.last")[0].get('href').split("/")[-1]
        for pagenum in range(1,int(num)):
            yield self.page_url.format(**locals())
        
    def _scrape_unit(self, article):
        article.prepare(self)
        postentry = self.clean_html(article.doc.cssselect("div.postEntry")[0])
        article.props.text = postentry.text_content()

        for comment in self.get_comments(article):
            comment.is_comment = True
            yield comment
        yield article


    def get_comments(self, article):
        for li in article.doc.cssselect("li.comment"):
            comment = HTMLDocument()
            comment.props.text = li.cssselect("div.comment-text")[0]
            
            pattern = re.compile("Geplaatst door ([\w ]+) op ([\w :]+)")
            result = pattern.search(
                li.cssselect("div.commentsbox span")[0].text_content()
                )
            comment.props.author = result.group(1)
            comment.props.date = readDate(result.group(2))
            comment.parent = article
            yield comment


        
    def clean_html(self, html):
        html.cssselect("p.similarposts")[0].drop_tree()
        [s.drop_tree() for s in html.cssselect("script")]
        html.cssselect("div.clearfix")[0].drop_tree()
        html.cssselect("p.reader")[0].drop_tree()
        return html

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Gezondheid_blog_nlScraper)
