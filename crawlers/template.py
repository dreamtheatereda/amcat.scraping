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
from amcat.scraping.scraper import Crawler, AuthCrawler
import re
#AuthCrawler is for login

class TemplateCrawler(Crawler):
    medium_name = "Template"

    allow_url_patterns = [
        ex1 = re.compile("^http://www.example.com/\d+/"),
        ex2 = re.compile("krant.example.com/"),
        ] #anything goes

    ignore_url_patterns = [
        ex1 = re.compile("/verkiezingen/per_gemeente/\w+/"),
        ] #anything goes, use for speed tweaks

    article_pattern = re.compile("/articles/[0-9]/[a-zA-Z0-9]")

    initial_urls = [
        "http://www.example.com",
        "http://krant.example.com"
        ]

    def __init__(self, *args, **kwargs):
        super(TemplateCrawler, self).__init__(*args, **kwargs)
        
    def _scrape_unit(self, url): 

        page = HTMLDocument(date = ipage.props.date,url=url)
        page.prepare(self)
        page.doc = self.getdoc(page.props.url)
        yield self.get_article(page)

    def get_article(self, page):
        #use mainly page.doc.cssselect() to fill the following lines
        page.props.author = 
        page.props.headline = 
        page.props.text = 
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TemplateCrawler) #change 'TemplateScraper'


