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
from urllib2 import HTTPError
from amcat.tools.toolkit import readDate
from datetime import datetime
from amcat.scraping.htmltools import create_cc_cookies

INDEX_URL = "http://www.volkskrant.nl/vk/nl/2/archief/integration/nmc/frameset/archive/archiveDay.dhtml?archiveDay={y:04d}{m:02d}{d:02d}"

from amcat.scraping.scraper import HTTPScraper,DatedScraper

class WebVolkskrantScraper(HTTPScraper, DatedScraper):
    medium_name = "Volkskrant website"

    def set_cookies(self):
        for cookie in create_cc_cookies(".volkskrant.nl"):
            self.opener.cookiejar.set_cookie(cookie)

    def _get_units(self):
        self.set_cookies()
        index_dict = {
            'y':self.options['date'].year,
            'm':self.options['date'].month,
            'd':self.options['date'].day
            }
        index = self.getdoc(INDEX_URL.format(**index_dict))
        for unit in index.cssselect('#hvdn_archief dd'):
            url = unit.cssselect("a")[0].get('href')
            unit.cssselect("span")[0].drop_tree()
            title = unit.cssselect("a")[0].text_content().strip("\"")
            yield HTMLDocument(url=url,headline=title)
 
        
    def _scrape_unit(self, page): 
        page.prepare(self)
        try:
            author = page.doc.cssselect("span.author")[0]
            if "OPINIE" in author.text:
                page.props.author = author.text.split("-")[1].strip()
            elif "Door:" in author.text:
                page.props.author = author.text.split("Door:")[1].strip()
            else:
                page.props.author = author.text
        except IndexError:
            try:
                time_post = page.doc.cssselect("div.time_post")[0].text
            except IndexError:
                return
            if "bron" in time_post:
                page.props.author = page.doc.cssselect("div.time_post")[0].text.split("bron:")[1]
            else:
                page.props.author = "None"
        if hasattr(page.props,"author"):
            if page.props.author:
                page.props.author = page.props.author[:98]
        page.props.text = page.doc.cssselect("#art_box2")[0].text_content()
        yield page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WebVolkskrantScraper)
