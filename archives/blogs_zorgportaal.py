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

INDEX_URL = "http://site.zorgportaal.nl/index.php/blogs-en-forums/blogs/toon-alle-blogs"
BASE_URL = "http://site.zorgportaal.nl"

from amcat.scraping.scraper import HTTPScraper

class Zorgportaal_nlBlogScraper(HTTPScraper):
    medium_name = "Zorgportaal.nl blogs"

    def __init__(self, *args, **kwargs):
        super(Zorgportaal_nlBlogScraper, self).__init__(*args, **kwargs)


    def _get_units(self):
        
        index = self.getdoc(INDEX_URL) 
        
        pages = [index] + [self.getdoc(urljoin(BASE_URL,p.get('href'))) for p in index.cssselect("ul.list-pagination li a")[:-1]]
                           
        for page in pages:
            units = page.cssselect('#ezblog-posts div.blog-post')
            for unit in units:
                date = unit.cssselect("time")[0].get('datetime')
                link = unit.cssselect('h2.blog-title a')[0].get('href')
                href = urljoin(BASE_URL,link)
                yield HTMLDocument(url=href, date=date)

                
    def _scrape_unit(self, page): 
        
        page.prepare(self)
        page.doc = self.getdoc(page.props.url)
        page.props.author = page.doc.cssselect("div.blog-meta span.blog-author a")[0].text
        page.props.text = page.doc.cssselect("#ezblog-body div.blog-text")[0].text_content()
        page.props.headline = page.doc.cssselect("h1.blog-title")[0].text
        yield page



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Zorgportaal_nlBlogScraper)


