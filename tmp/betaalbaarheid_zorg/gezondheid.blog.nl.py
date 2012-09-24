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
from amcat.scraping.document import HTMLDocument
from amcat.tools.toolkit import readDate

import re

INDEX_URL = "http://www.gezondheid.blog.nl"

class Gezondheid_blog_nlScraper(HTTPScraper, DatedScraper):
    medium_name = "gezondheid.blog.nl"

    def __init__(self, *args, **kwargs):
        super(Gezondheid_blog_nlScraper, self).__init__(*args, **kwargs)

    def _get_units(self):
        """get pages"""



        index = self.getdoc(INDEX_URL) 
        articles = index.cssselect('div.post')
        for article in articles:
            footer = article.cssselect("div.postInfo")[0].text.split("\t")[1]
            p = re.compile(r'^Door ([\D]+) op ([a-z0-9\s]+) om')
            _re = p.search(footer)
            author = _re.group(1)
            date = readDate(_re.group(2))
            headline = article.cssselect("h1")[0].text_content()
            if str(self.options['date']) not in str(date):
                break
            link = article.cssselect("h1 a")[0].get('href')
            yield HTMLDocument(url=link,headline=headline,author=author)
        
        
    def _scrape_unit(self, doc):
        doc.prepare(self)
        doc.doc = self.getdoc(doc.props.url)
        doc.props.text = doc.doc.cssselect("div.post div.postEntry")[0].text_content()
        doc.props.source = doc.doc.cssselect("div.post div.postEntry p em a")[0].get('href')
        yield doc




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Gezondheid_blog_nlScraper)
