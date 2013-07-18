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

from urlparse import urljoin

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate

class NewsAtScraper(HTTPScraper, DatedScraper):
    medium_name = "news.at"
    index_url = "http://news.at/archiv/{self.options[date].year}/{self.options[date].month}/{self.options[date].day}"
    page_url = "http://www.news.at/archiv/{self.options[date].year}/{self.options[date].month}/{self.options[date].day}?a.p%5B0%5D={pagenr}"

    def _get_units(self):
        index_url = self.index_url.format(**locals());index = self.getdoc(index_url)
        for page in self.get_pages(index):
            for li in page.cssselect("section.articles ul.line li"):
                article = HTMLDocument(
                    url = urljoin(index_url, li.cssselect("a")[0].get('href')),
                    headline = li.cssselect("h3 a")[0].text_content().strip(),
                    byline = li.cssselect("p.intro") and li.cssselect("p.intro")[0].text_content().strip(),
                    date = readDate(li.cssselect("time")[0].get('datetime')))
                article.props.kicker = li.cssselect("a.toprow")[0].text_content().strip()
                yield article
                    
    def get_pages(self, index):
        yield index
        max_page = int(index.cssselect("div.section_wrapper div.pager li a")[-1].text)
        for pagenr in range(2, max_page + 1):
            yield self.getdoc(self.page_url.format(**locals()))
            
    def _scrape_unit(self, article):
        article.prepare(self)
        subsection = article.doc.cssselect("#topnews header.title a")
        if article.doc.cssselect("header.main nav li.active a"):
            headsection = article.doc.cssselect("header.main nav li.active a")[0].text
            article.props.section = subsection and headsection + " > " + subsection[0].text or headsection
        else:
            article.props.section = subsection and subsection[0].text or None
        article.props.externalid = article.doc.cssselect("#main article")[0].get('data-id')
        article.props.text = article.doc.cssselect("div.ym-gr")[0].cssselect("p")
        article.props.author = article.doc.cssselect("span.author")
        yield article
            
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(NewsAtScraper)


