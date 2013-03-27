# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
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

import re
import datetime
from urlparse import urljoin

from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.scraping.document import HTMLDocument
from amcat.scraping.htmltools import create_cc_cookies

from amcat.tools import toolkit
from amcat.tools.toolkit import readDate

INDEX_URL = "http://www.parool.nl"
CONTENT_URL = "http://www.parool.nl/parool/article/pagedListContent.do?language=nl&navigationItemId={nid}&navigation={n}&page={p}"

class ParoolScraper(HTTPScraper, DatedScraper):
    medium_name = "Parool website"
    def _set_cookies(self):
        for cookie in create_cc_cookies(".parool.nl"):
            self.opener.cookiejar.set_cookie(cookie)

    def _get_units(self):
        self._set_cookies()

        homepage = self.getdoc(INDEX_URL)
        for index in homepage.cssselect("div.art_box8_list h3 a"):
            i_url = urljoin(INDEX_URL,index.get('href'))
            indexpage = self.getdoc(i_url)
            link = indexpage.cssselect("div.gen_box3 h2 a")[0].get('href')
            url_contents = {
                'p':0,
                'nid':i_url.split("/")[5],
                'n':i_url.split("/")[6]
                }
            doc = self.getdoc(CONTENT_URL.format(**url_contents))
            while True:
                stop=False
                for node in doc.cssselect("ul.list_node"):
                    artdate = readDate(node.cssselect("p a")[0].text.strip(")(")).date()
                    if artdate > self.options['date']:
                        pass
                    elif artdate == self.options['date']:
                        href = node.cssselect("a")[0].get('href')
                        yield HTMLDocument(url=urljoin(INDEX_URL,href))
                    elif artdate < self.options['date']:
                        stop=True;break
                if stop == True:
                    break
                else:
                    href = doc.cssselect("div.gen_box3 a")[-1].get('href')
                    doc = self.getdoc(urljoin(INDEX_URL,href))
            

    def _scrape_unit(self,page):
        page.prepare(self)
        page.props.headline = page.doc.cssselect("#art_box2 h1")[0].text_content()
        page.props.author = page.doc.cssselect("div.time_post")[0].text.split(":")[-1].strip()
        for script in page.doc.cssselect("script"):
            script.drop_tree()
        for h1 in page.doc.cssselect("h1"):
            h1.drop_tree()
        page.props.text = page.doc.cssselect("#art_box2")[0]
        page.props.date = readDate(page.doc.cssselect("div.time_post")[0].text.split("Bron:")[0])
        page.props.section = re.search("parool/nl/[0-9]+/([A-Z\-]+)/article", page.props.url).group(1).capitalize()
        yield page




if __name__ == '__main__':
    import sys
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(ParoolScraper)
