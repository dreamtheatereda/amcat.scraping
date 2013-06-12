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
import time

FRONTPAGE_URL = "http://frontpage.fok.nl"
INDEX_URL = "http://frontpage.fok.nl/nieuws/archief/{y:04d}/{m:02d}/{d:02d}"

class FokScraper(HTTPScraper, DatedScraper):
    medium_name = "fok nieuws"

    def _cookie(self):
        page = self.open(FRONTPAGE_URL)
        cookie_string = page.info()["Set-Cookie"]
        token = cookie_string.split(";")[0]
        self.opener.opener.addheaders.append(("Cookie",token+"; allowallcookies=1"))
        self.open(FRONTPAGE_URL)


    def _get_units(self):
        for x in range(3):
            try:
                self._cookie()
            except:
                print('Error 503 at _cookie function, trying again in a minute...')
                time.sleep(60)
            else:
                break
                
            
        index_dict = {
            'y' : self.options['date'].year,
            'm' : self.options['date'].month,
            'd' : self.options['date'].day
        }

        url = INDEX_URL.format(**index_dict)

        for x in range(3):
            try:
                index = self.getdoc(url)
            except Exception:
                time.sleep(5)
            else:
                break
        
        articles = index.cssselect('.title')
        for article_unit in articles:
            href = article_unit.cssselect('a')[0].get('href')
            yield HTMLDocument(url=href, date=self.options['date'])

    def _scrape_unit(self, page):
        for x in range(3):
            try:
                page.prepare(self)
            except Exception:
                time.sleep(5)
            else:
                break
        page.props.section = page.props.url.split("/")[3]
        bodyparts = page.doc.cssselect("div.itemBody")[0]
        page.props.text = bodyparts.text_content().split('Lees ook:\n')[0].strip()
        page.props.headline = page.doc.cssselect("h1.title")[0].text.strip("\n")
        byline = page.doc.cssselect("span.postedbyline")[0].text_content()
        page.props.author = byline[byline.find("Geschreven door")+16:byline.find(" op ")]
        page.props.date = readDate(page.doc.cssselect("span.postedbyline")[0].text_content().split(" op ")[1])
        for comment in self.get_comments(page):
            comment.is_comment = True
            yield comment
        yield page

    def get_comments(self,page):
        
        for div in page.doc.cssselect("div.reactieHolder"):
            comment = HTMLDocument()
            comment.props.author = div.cssselect("span.left a")[0].text
            comment.props.date = readDate(div.cssselect("a.timelink")[0].text)
            comment.props.text = div.cssselect("div.reactieBody")[0]
            comment.props.parent = page
            yield comment



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(FokScraper)

