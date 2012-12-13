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
from amcat.tools.toolkit import readDate


INDEX_URL = "http://www.telegraaf.nl/snelnieuws/"

from datetime import date as _date
from amcat.scraping.scraper import HTTPScraper,DatedScraper

class WebTelegraafScraper(HTTPScraper, DatedScraper):
    medium_name = "Telegraaf website"

    def __init__(self, *args, **kwargs):
        super(WebTelegraafScraper, self).__init__(*args, **kwargs)


    def _get_units(self):
        
        index = self.getdoc(INDEX_URL) 
        for section in index.cssselect("#main li.naar a"):
            
            date = _date.today()
            href = urljoin("http://www.telegraaf.nl",section.get('href'))
            if "digitaal/games" in href:
                continue


            ipage = self.getdoc(href)
            print(href)
            while date >= self.options['date']:
                for unit in ipage.cssselect('#main ul.snelnieuws_list li.item'):
                    href = unit.cssselect('a')[0].get('href')
                    article = HTMLDocument(url=href)
                    article.doc = self.getdoc(article.props.url)
                    try:
                        date = readDate(article.doc.cssselect("span.datum")[0].text).date()
                    except IndexError:
                        continue
                    if date == self.options['date']:
                        yield article
                    elif date < self.options['date']:
                        break


                nxt = ipage.cssselect("#main li.sn_navigation a")[0]
                if "vorige" in nxt.text:
                    print("\nNo articles found for given date.\n")
                elif "games" in href:
                    break
                else:
                    nxt_url = urljoin("http://www.telegraaf.nl",nxt.get('href'))
                    ipage = self.getdoc(nxt_url)






        
    def _scrape_unit(self, page): 
        page.prepare(self)
        page.props.date = readDate(page.doc.cssselect("span.datum")[0].text_content())
        page.props.author = "Unknown"
        page.props.headline = page.doc.cssselect("#artikel h1")[0].text_content().strip()
        page.doc.cssselect("div.broodMediaBox")[0].drop_tree()
        page.props.text = page.doc.cssselect("#artikelKolom")[0].text_content()
        page.props.section = page.doc.cssselect("#breadcrumbs a")[-1].text

        for comment in self.scrape_comments(page):
            yield comment

        yield page


    def scrape_comments(self,page):
        p = page.props.url+"?page={}"
        if not page.doc.cssselect("ul.pager"):
            return
        total = int(page.doc.cssselect("ul.pager li.pager-last a")[0].get('href').split("page=")[-1].split("&")[0]) + 1
        docs = [self.getdoc(p.format(x)) for x in range(total)]
        for doc in docs:
            for div in doc.cssselect("#comments div.comment"):
                comment = Document()
                comment.props.text = div.cssselect("div.content")[0].text_content()
                comment.props.author = div.cssselect("span.submitted-username")[0].text_content()
                comment.props.date = readDate(div.cssselect("div.submitted div.floatr")[0].text_content())
                comment.parent = page
                yield comment



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WebTelegraafScraper)


