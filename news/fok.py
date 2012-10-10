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
from amcat.scraping.document import HTMLDocument, IndexDocument





FRONTPAGE_URL = "http://frontpage.fok.nl"
INDEX_URL = "http://frontpage.fok.nl/nieuws/archief/{y:04d}/{m:02d}/{d:02d}"

class FokScraper(HTTPScraper, DatedScraper):
    medium_name = "fok nieuws"

    def __init__(self, *args, **kwargs):
        
        super(FokScraper, self).__init__(*args, **kwargs)

    def _cookie(self):

        page = self.opener.opener.open(FRONTPAGE_URL)

        cookie_string = page.info()["Set-Cookie"]
        token = cookie_string.split(";")[0]
        self.opener.opener.addheaders.append(("Cookie",token+"; allowallcookies=1"))
        page = self.opener.opener.open(FRONTPAGE_URL)


    def _get_units(self):
        """papers are often organised in blocks (pages) of articles, this method gets the blocks, articles are to be gotten later"""
        self._cookie()
        index_dict = {
            'y' : self.options['date'].year,
            'm' : self.options['date'].month,
            'd' : self.options['date'].day
        }

        url = INDEX_URL.format(**index_dict)
        index = self.getdoc(url)
        articles = index.cssselect('.title')
        for article_unit in articles:
            href = article_unit.cssselect('a')[0].get('href')
            yield HTMLDocument(url=href, date=self.options['date'])

    def _scrape_unit(self, page):
        """units are articles here, not pages"""
        page.prepare(self)
        page.page = ""
        page.doc = self.getdoc(page.props.url)
        txt = ""
        for paragraph in page.doc.cssselect("div.itemBody p"):
            try:
                txt += (paragraph.text+"\n")
            except TypeError: #empty paragraph
                pass
        page.props.text = txt
        byline = page.doc.cssselect("span.postedbyline")[0].text_content()
        page.props.author = byline[byline.find("Geschreven door")+16:byline.find(" op ")]
        page.props.headline = page.doc.cssselect("h1.title")[0].text.strip("\n")

        
        yield page



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(FokScraper)

