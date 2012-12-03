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

from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument
from amcat.scraping import toolkit as stoolkit
import time
from urllib import urlencode


INDEX_URL = "http://digitaal.ddl.x-cago.net/DDL/{:%Y%m%d}/public/index_tablet.html"
PAGE_URL = "http://digitaal.ddl.x-cago.net/DDL/{:%Y%m%d}/public/{pageurl}_tablet.html"
ARTICLE_URL = "http://digitaal.ddl.x-cago.net/DDL/{:%Y%m%d}/public/pages/{pageid}/articles/{articleid}_body_tablet.html"
LOGIN_URL = "http://mgl.x-cago.net/login.do?pub=ddl&auto=false"

class LimburgerScraper(HTTPScraper, DBScraper):
    medium_name = "De Limburger"

    def __init__(self, *args, **kwargs):
        super(LimburgerScraper, self).__init__(*args, **kwargs)


    def _login(self, username, password):
        """log in on the web page
        @param username: username to log in with
        @param password: password 
        """

        page = self.getdoc(LOGIN_URL)
        form = stoolkit.parse_form(page)
        form['email'] = username
        form['password'] = password
        page = self.opener.opener.open(LOGIN_URL, urlencode(form))

    def _get_pages_links(self,page):
        JS_text = page.text_content()
        lines = JS_text.split(";")
        pages = []
        for line in lines:
            if "pageTable.add( \"DDL" in line and not "Advertentie" in line:
                args = line[line.find("Array"):].split(",")
                pages.append({'date' : args[1],'link' : args[2].strip().strip('"').lstrip("/"),'pagenum' : args[3],'category' : args[6]})
        return pages

    def _get_units(self):
        """get pages"""

        index_url = INDEX_URL.format(self.options['date'])
        print(index_url)
        index = self.getdoc(index_url)
        
        for page in self._get_pages_links(index):
            url = PAGE_URL.format(self.options['date'],pageurl = page['link'])
            yield url

        
    def _scrape_unit(self, url):
        doc = self.getdoc(url)
        pageid = url.split("/")[-2]
        for article in doc.cssselect("body div.overlay"):

            text = article.text_content()
            onclick = text[text.find("onClick"):]
            article_id = onclick.split(",")[0].split("'")[1]
            url = ARTICLE_URL.format(self.options['date'],pageid = pageid,articleid = article_id)
            
            page = HTMLDocument(date = self.options['date'], url = url)
            page.prepare(self)
            page.doc = self.getdoc(page.props.url)
            yield self.get_article(page)


    def get_article(self, page):
        try: #not always an author in text
            page.props.author = page.doc.cssselect("font.artauthor")[0].text.lstrip("dor")[0:98]
        except IndexError:
            pass
        page.props.headline = page.doc.cssselect("font.artheader")[0].text
        page.props.text = page.doc.cssselect("font.artbody")[0].text_content()
        page.coords=""
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(LimburgerScraper)


