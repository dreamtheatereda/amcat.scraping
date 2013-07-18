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
from urlparse import urljoin

INDEX_URL = "http://vagz.nl/index.php/the-news"

class Vagz_nlScraper(HTTPScraper, DatedScraper):
    medium_name = "vagz.nl"

    def __init__(self, *args, **kwargs):
        super(Vagz_nlScraper, self).__init__(*args, **kwargs)


    def _get_units(self):

      
        index = self.getdoc(INDEX_URL) 
        pages = [INDEX_URL] + [urljoin(INDEX_URL,l.get('href')) for l in index.cssselect("ul.pagination li a")[3:]]
        for p in pages:
            doc = self.getdoc(p)
            articles = doc.cssselect('table.contentpane tr.sectiontableentry2')
            articles2 = doc.cssselect('table.contentpane tr.sectiontableentry1')
            articles.extend(articles2)
            for article in articles:
                date = article.cssselect('td')[2].text
                if str(self.options['date']) in str(readDate(date)):
                    link = article.cssselect('td')[1].cssselect('a')[0].get('href')
                    href = urljoin(INDEX_URL,link)
                    yield HTMLDocument(url=href, date=readDate(date))





    def noscript(self,html):
        for script in html.cssselect("script"):
            script.drop_tree()
        return html
        
    def _scrape_unit(self, page):
        page.prepare(self)
        page.props.headline = page.doc.cssselect("h2.contentheading")[0].text_content().strip()
        page.props.text = self.noscript(page.doc.cssselect("div.article-content")[0]).text_content()
        for a in page.doc.cssselect("div.article-content a"):
            if a.text.strip(" .").lower() == "lees verder":
                page.props.source = a.text

        yield page

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Vagz_nlScraper)



