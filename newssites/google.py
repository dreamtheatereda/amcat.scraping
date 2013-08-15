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
from lxml import html

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate

class GoogleNewsScraper(HTTPScraper, DatedScraper):
    """To be inherited from. 
    It is advised that this scraper runs hourly, as most articles don't last as long as a day.
    It is also advised that the set be deduplicated after scraping."""
    medium_name = "Google News"

    def __init__(self, *args, **kwargs):
        super(GoogleNewsScraper, self).__init__(*args, **kwargs)
        self.index_url = "http://news.google." + self.url_gtld

    def _get_units(self):
        index = self.getdoc(self.index_url)
        for section_doc in self.sections(index):
            rss_url = section_doc.cssselect("div.footer div.bottom div.links a")[0].get('href')
            rss_index = self.getdoc(rss_url)
            for item in rss_index.cssselect("item"):
                html_content = html.fromstring(item.cssselect("description")[0].text)
                all_sources_url = html_content.cssselect("a.p")[-1].get('href')
                all_sources_doc = self.getdoc(all_sources_url + "&output=rss")
                for _item in all_sources_doc.cssselect("item"):
                    date = readDate(_item.cssselect("pubdate")[0].text)
                    if date.date() == self.options['date']:
                        yield _item

    def sections(self, index):
        for a in index.cssselect("#nav-menu-wrapper li.nav-item a"):
            url = urljoin(self.index_url, a.get('href'))
            section = a.text
            yield self.getdoc(url)

    def _scrape_unit(self, xmlitem):
        html_content = html.fromstring(xmlitem.cssselect("description")[0].text)
        url = xmlitem.cssselect("link")[0].tail.split("&url=")[-1]
        article = HTMLDocument(url = url)
        article.props.headline = " - ".join(xmlitem.cssselect("title")[0].text.split(" - ")[:-1])
        article.props.source = xmlitem.cssselect("title")[0].text.split(" - ")[-1]
        article.props.section = xmlitem.cssselect("category")[0].text
        article.props.date = readDate(xmlitem.cssselect("pubdate")[0].text)
        article.props.snippet = html_content.cssselect("div.lh font")[1].text
        try:
            article.prepare(self)
        except Exception:
            yield article;return
        article.props.html = html.tostring(article.doc)
        yield article

            
if __name__ == '__main__':
    raise Exception("Please inherit from this scraper")


